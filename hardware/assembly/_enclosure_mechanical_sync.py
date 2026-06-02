"""Doc-sync driver for hardware/assembly/enclosure-mechanical.md.

Run: tools/cad-venv/bin/python hardware/assembly/_enclosure_mechanical_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "back-panel"))
sys.path.insert(0, str(_hw / "cut-parts" / "compressor-shroud"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core"))

from _back_panel_dimensions import (  # noqa: E402
    ac_inlet_recess_depth_max,
    ac_inlet_recess_depth_min,
)
from _compressor_shroud_dimensions import (  # noqa: E402
    panel_hole_label,
    terminal_block_clearance_mm,
    wall_thickness_in,
)
from _cold_core_interface import (  # noqa: E402
    outer_shell_x_length,
    outer_shell_y_length,
)
from docgen import substitute_md  # noqa: E402


def main():
    variables = {
        # AC inlet recess range.
        "AC_RECESS_DEPTH": (
            f"{ac_inlet_recess_depth_min:.4g}–{ac_inlet_recess_depth_max:.4g} mm"
        ),
        # Terminal-block min clearance inside the shroud.
        "TB_CLEARANCE": f"{terminal_block_clearance_mm:.4g} mm",
        # G90 sheet thickness.
        "WALL_IN": f'{wall_thickness_in:.4g}"',
        # Heyco SB-500-6 sidewall panel hole.
        "PANEL_HOLE": panel_hole_label,
        # Foam-shell outer bottom-cap footprint.
        "FOAM_SHELL_X": f"{outer_shell_x_length:.4g}",
        "FOAM_SHELL_Y": f"{outer_shell_y_length:.4g} mm",
    }

    substitute_md(
        _here / "enclosure-mechanical.md",
        variables=variables,
        expected_counts={
            "AC_RECESS_DEPTH": 2,
            "TB_CLEARANCE": 1,
            "WALL_IN": 1,
            "PANEL_HOLE": 3,
            "FOAM_SHELL_X": 1,
            "FOAM_SHELL_Y": 1,
        },
    )
    print("-> enclosure-mechanical.md")


if __name__ == "__main__":
    main()
