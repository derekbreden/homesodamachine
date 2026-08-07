"""Doc-sync driver for hardware/printed-parts/enclosure/back-panel/README.md.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from docgen import substitute_md


# AC inlet recess: an IEC 60320 C14 receptacle nests into the panel face,
# the mating C13 cord housing ending flush with the panel surface. The
# depth range lets the C13 housing nest without bottoming on the bezel.
ac_inlet_recess_depth_min = 3.0
ac_inlet_recess_depth_max = 5.0

# Bulkhead panel-hole diameter. All four PP1208E bulkheads on this
# panel (1 water inlet + 3 umbilical-port unions) share this hole —
# the bore enclosure.py cuts (struck in manifold-layout/front_half.py's
# `back_wall_ports`, the cutting source), sized to clear
# the Ø17.14 barrel measured off the jg-bulkhead-union reference STEP.
# JG's catalog nominal (0.67" ≈ 17.0) sits under the measured barrel.
bulkhead_panel_hole_diameter = 18.0


def main():
    variables = {
        "AC_RECESS_DEPTH": f"{ac_inlet_recess_depth_min:.4g}–{ac_inlet_recess_depth_max:.4g} mm",
        "PANEL_HOLE_D": f"{bulkhead_panel_hole_diameter:.1f} mm",
        "PANEL_HOLE_D_SHORT": f"{bulkhead_panel_hole_diameter:.4g}",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "AC_RECESS_DEPTH": 2,
            "PANEL_HOLE_D": 2,
            "PANEL_HOLE_D_SHORT": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
