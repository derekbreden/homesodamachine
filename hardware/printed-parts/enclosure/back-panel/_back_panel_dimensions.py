"""Rear-panel dimensions — the named constants that the README's prose
refers to. No CAD geometry yet (this part is still design-in-progress);
this module is the source-of-truth for the dimensional numbers cited in
README.md until the panel reaches a CAD generator.

Run this module directly to substitute the values into README.md."""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from docgen import substitute_md


# AC inlet recess (IEC 60320 C14 receptacle nests into the panel face so
# the C13 cord housing ends flush with the panel surface). The range is
# the design window — anywhere in here lets the C13 housing nest without
# bottoming out on the bezel.
ac_inlet_recess_depth_min = 3.0
ac_inlet_recess_depth_max = 5.0

# Bulkhead panel-hole diameter — the John Guest 1/4" body family
# (PI1208S water inlet + PP1208E umbilical-port unions) all share this
# panel-hole spec. JG catalog spec for the 1/4" body family (0.67").
# Mirrors the value used by the reservoir cap on the cold-core
# (bulkhead_panel_hole_diameter in cold-core/reservoir/
# reservoir.py) — same bulkhead family, same panel hole.
# Not imported from the cold-core because that value lives inside the
# reservoir generator's local scope, not in _cold_core_interface.py.
bulkhead_panel_hole_diameter = 17.0


def main():
    variables = {
        # AC inlet recess range — rendered as the same "3–5 mm" string
        # in both places it appears, so a single variable suffices.
        "AC_RECESS_DEPTH": f"{ac_inlet_recess_depth_min:g}–{ac_inlet_recess_depth_max:g} mm",
        # Bulkhead panel-hole diameter. Two rendering forms: "17.0 mm"
        # in the connections-inventory table (matches the precision the
        # JG catalog quotes) and "17" in the open-items prose.
        "PANEL_HOLE_D": f"{bulkhead_panel_hole_diameter:.1f} mm",
        "PANEL_HOLE_D_SHORT": f"{bulkhead_panel_hole_diameter:g}",
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
