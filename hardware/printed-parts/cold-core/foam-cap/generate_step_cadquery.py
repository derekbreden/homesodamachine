"""Foam-cap stack — the three parts that close one end of the
foam shell during the pour-in-place foam cure: the cap tray, the
lid that sits atop the cap during pouring, and the TPU 90A gasket
that compresses between the cap and the outer-shell mating face.
Printed twice per build (one stack on each end of the shell)."""

import sys
from pathlib import Path

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
)


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
    from the shell's −Z support arch up through the top cap. The cut
    starts 5 mm below the cap floor and extends past the cap roof so
    OCCT subtracts cleanly through both faces."""
    margin = 5.0
    return cap.cut(
        build_a_y_axis_hole_punch(
            origin=(0, -margin, co2_inlet_z),
            hole_punch_height=foam_cap_height + 2 * margin,
        )
    )


def main():
    cap = build_foam_cap()
    cap_top = cut_co2_inlet(cap)
    cap_bottom = cap
    lid = build_foam_cap_lid()
    gasket = build_foam_cap_gasket()

    # Sanity check: the cap is a 2 mm floor + 2 mm perimeter shell, so
    # at (x=0, z=co2_inlet_z) — well inside the perimeter — the hole
    # only pierces the floor. Expected removed volume is a ⌀6.5
    # cylinder of length wall_and_floor_thickness (one floor pass).
    expected_hole_volume = 3.14159265358979 * 3.25 ** 2 * wall_and_floor_thickness
    actual_volume_diff = cap_bottom.val().Volume() - cap_top.val().Volume()
    print(f"co2_inlet_z = {co2_inlet_z}")
    print(f"cap_bottom.Volume() - cap_top.Volume() = {actual_volume_diff:.3f}")
    print(f"expected ⌀6.5 × {wall_and_floor_thickness} mm cylinder = {expected_hole_volume:.3f}")

    export_step(cap_top, str(_here / "foam-cap-top.step"))
    export_step(cap_bottom, str(_here / "foam-cap-bottom.step"))
    export_step(lid, str(_here / "foam-cap-lid.step"))
    export_step(gasket, str(_here / "foam-cap-gasket.step"))
    print("-> foam-cap-top.step")
    print("-> foam-cap-bottom.step")
    print("-> foam-cap-lid.step")
    print("-> foam-cap-gasket.step")


if __name__ == "__main__":
    main()
