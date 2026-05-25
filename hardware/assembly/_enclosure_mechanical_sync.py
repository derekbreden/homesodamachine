"""Sync the named dimensional values in `enclosure-mechanical.md` against
the canonical source modules that already own them.

This assembly doc is a production-cadence wrapper around several part-level
README sources of truth: the back-panel (AC inlet recess), the front-panel
(currently no shared scalars cited here), the nameplate (currently none
cited here), the compressor shroud (terminal-block clearance, sheet
thickness, Heyco bushing panel-hole size), and the foam shell (outer
bottom-cap footprint pulled live through `_cold_core_interface`). Each
NAME below points back to whichever upstream dimensions module defines it;
this script is the only place the assembly doc's prose is kept in sync.

Run as a script to substitute the README:

    tools/cad-venv/bin/python _enclosure_mechanical_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

# Each dimension module lives in its own directory; add each directory to
# sys.path so the bare-module imports below resolve.
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
    outer_shell_z_length,
)
from docgen import substitute_md  # noqa: E402


def main():
    variables = {
        # AC inlet recess range — same "3–5 mm" rendering as back-panel.
        "AC_RECESS_DEPTH": (
            f"{ac_inlet_recess_depth_min:g}–{ac_inlet_recess_depth_max:g} mm"
        ),
        # Terminal-block min clearance inside the shroud.
        "TB_CLEARANCE": f"{terminal_block_clearance_mm:g} mm",
        # G90 sheet thickness — rendered with inch units to match the
        # SendCutSend catalog spelling in the compressor-shroud README.
        "WALL_IN": f'{wall_thickness_in:g}"',
        # Heyco SB-500-6 sidewall panel hole; reads better as the inch
        # fraction (1/2") than the decimal (0.5"), matching shroud usage.
        "PANEL_HOLE": panel_hole_label,
        # Foam-shell outer bottom-cap footprint — pulled live from the
        # cold-core interface so any shift in the foam shell propagates
        # here on the next run. Same "g" formatting as the enclosure
        # README's FOAM_SHELL_X / FOAM_SHELL_Z (no units inside each
        # variable so the prose's "× 181 mm" reads naturally).
        "FOAM_SHELL_X": f"{outer_shell_x_length:g}",
        "FOAM_SHELL_Z": f"{outer_shell_z_length:g} mm",
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
            "FOAM_SHELL_Z": 1,
        },
    )
    print("-> enclosure-mechanical.md")


if __name__ == "__main__":
    main()
