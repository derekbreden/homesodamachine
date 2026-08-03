"""Doc-sync driver for hardware/assembly/enclosure-mechanical.md.

Run: tools/cad-venv/bin/python hardware/assembly/_enclosure_mechanical_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "enclosure-assembly"))
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
import _contents as _contents  # noqa: E402  — the rear port row's own stations and hardware
from docgen import substitute_md  # noqa: E402


def _port_chain(n):
    """The panel width n adjacent bulkhead nuts occupy, margins included."""
    return n * _contents.PORT_NUT_D + (n - 1) * _contents.PORT_NUT_GAP


def main():
    _umbilical = " / ".join(
        f"{_contents.back_port_station(n)[0]:.4g}"
        for n in ("bulkhead-flavor-b", "bulkhead-carb", "bulkhead-flavor-a"))
    variables = {
        # AC inlet recess range.
        "AC_RECESS_DEPTH": (
            f"{ac_inlet_recess_depth_min:.4g}–{ac_inlet_recess_depth_max:.4g} mm"
        ),
        # Terminal-block min clearance inside the shroud.
        "TB_CLEARANCE": f"{terminal_block_clearance_mm:.4g} mm",
        # G90 sheet thickness.
        "WALL_IN": f'{wall_thickness_in:.4g}"',
        # AC pass-through panel hole (cable gland).
        "PANEL_HOLE": panel_hole_label,
        # Foam-shell outer bottom-cap footprint.
        "FOAM_SHELL_X": f"{outer_shell_x_length:.4g}",
        "FOAM_SHELL_Y": f"{outer_shell_y_length:.4g}",
        # The rear port row: its hardware, what a chain of it occupies, and its stations.
        "PORT_NUT_D": f"{_contents.PORT_NUT_D:.4g}",
        "C14_FLANGE_W": f"{_contents.PORT_C14_FLANGE_W:.4g}",
        "PORT_CHAIN_4": f"{_port_chain(4):.4g}",
        "PORT_CHAIN_3": f"{_port_chain(3):.4g}",
        "PORT_ROW_Z": f"{_contents.port_row_z():.4g}",
        "WATER_BACK_X": f"{_contents.WATER_BACK_X:.4g}",
        "UMBILICAL_STATIONS": _umbilical,
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
            "PORT_NUT_D": 1,
            "C14_FLANGE_W": 1,
            "PORT_CHAIN_4": 1,
            "PORT_CHAIN_3": 1,
            "PORT_ROW_Z": 1,
            "WATER_BACK_X": 1,
            "UMBILICAL_STATIONS": 1,
        },
    )
    print("-> enclosure-mechanical.md")


if __name__ == "__main__":
    main()
