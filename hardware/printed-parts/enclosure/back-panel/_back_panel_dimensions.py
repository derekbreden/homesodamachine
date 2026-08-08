"""Doc-sync driver for hardware/printed-parts/enclosure/back-panel/README.md.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
sys.path.insert(0, str(_hw / "manifold-layout"))
sys.path.insert(0, str(_hw / "reference" / "jg-bulkhead-union"))
sys.path.insert(0, str(_hw / "reference" / "derpipe-co2-inlet"))

import front_half as _fh  # noqa: E402  — the pack, and the slip its wall is bored at
import derpipe_co2_inlet as _derpipe  # noqa: E402
import jg_bulkhead_union as _jg  # noqa: E402
from docgen import substitute_md  # noqa: E402


# AC inlet recess: an IEC 60320 C14 receptacle nests into the panel face,
# the mating C13 cord housing ending flush with the panel surface. The
# depth range lets the C13 housing nest without bottoming on the bezel.
# Typed, because the recess has no CAD — there is nothing yet to read it off.
ac_inlet_recess_depth_min = 3.0
ac_inlet_recess_depth_max = 5.0

# Bulkhead panel-hole diameter. All four PP1208E bulkheads on this panel
# (1 water inlet + 3 umbilical-port unions) share this hole. Read the way
# `front_half.back_wall_ports` — the cutting source enclosure.py bores from —
# strikes it: the barrel measured off the jg-bulkhead-union reference STEP,
# one `PORT_HOLE_SLIP` over on the diameter.
bulkhead_panel_hole_diameter = _jg.panel_hole_d(_fh.PORT_HOLE_SLIP)

# The CO2 station's hole, read the way `front_half.co2_wall_port` strikes it:
# the DERPIPE's own 1/4" NPT shank with one `PORT_HOLE_SLIP` on each side.
co2_panel_hole_diameter = _derpipe.SHANK_D + 2 * _fh.PORT_HOLE_SLIP


def main():
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
