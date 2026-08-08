"""Doc-sync driver for hardware/printed-parts/enclosure/back-panel/README.md.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
sys.path.insert(0, str(_hw / "manifold-layout"))

import front_half as _fh  # noqa: E402  — the wall's bores, off the calls that strike them
from docgen import substitute_md  # noqa: E402


# AC inlet recess: an IEC 60320 C14 receptacle nests into the panel face,
# the mating C13 cord housing ending flush with the panel surface. The
# depth range lets the C13 housing nest without bottoming on the bezel.
# Typed, because the recess has no CAD — there is nothing yet to read it off.
ac_inlet_recess_depth_min = 3.0
ac_inlet_recess_depth_max = 5.0

def panel_hole_diameters():
    """The two bores this panel carries: `(bulkhead, co2)`.

    Taken from the functions that STRIKE them, not from a second copy of their
    arithmetic. `front_half.back_wall_ports` and `front_half.co2_wall_port` are the
    calls `front_half.pack` fills `back_ports` with, and `enclosure._port_cuts` bores
    that list — so these are the holes that get cut, and a change to HOW either is
    struck (a chamfer allowance, a different slip for gas than for water) arrives here
    instead of leaving the README quoting the old rule.

    Both strike against a placed fitting, so both want the pack. That is why this is a
    function and not a module constant: the reading costs a build, and the two drivers
    that import this module for the AC recess must not pay for one.

    All four PP1208E bulkheads on this panel — 1 water inlet + 3 umbilical-port unions —
    share one hole, which is the figure the README quotes.
    """
    a = _fh.build_pack()
    bores = _fh.back_wall_ports(a.bulkhead_carry, *a.panel_carries.values())
    diameters = {round(p[3], 6) for p in bores}
    if len(diameters) != 1:
        raise ValueError(
            f"the four panel unions are bored at {sorted(diameters)}. The README gives them "
            f"one hole, so either they go back on one diameter or it reads them out apiece.")
    return bores[0][3], _fh.co2_wall_port(a.co2_inlet_carry)[3]


def main():
    bulkhead_panel_hole_diameter, co2_panel_hole_diameter = panel_hole_diameters()
    variables = {
        "AC_RECESS_DEPTH": f"{ac_inlet_recess_depth_min:.4g}–{ac_inlet_recess_depth_max:.4g} mm",
        "PANEL_HOLE_D": f"{bulkhead_panel_hole_diameter:.1f} mm",
        "PANEL_HOLE_D_SHORT": f"{bulkhead_panel_hole_diameter:.4g}",
        "CO2_HOLE_D": f"{co2_panel_hole_diameter:.4g}",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "AC_RECESS_DEPTH": 2,
            "PANEL_HOLE_D": 2,
            "PANEL_HOLE_D_SHORT": 1,
            "CO2_HOLE_D": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
