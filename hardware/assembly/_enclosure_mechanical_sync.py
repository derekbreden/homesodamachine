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
sys.path.insert(0, str(_hw / "manifold-layout"))
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "back-panel"))
sys.path.insert(0, str(_hw / "cut-parts" / "compressor-shroud"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_hw / "reference" / "jg-bulkhead-union"))
sys.path.insert(0, str(_hw / "reference" / "iec-c14-inlet"))

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
import front_half as _fh  # noqa: E402  — the rear port row's own placed unions
import iec_c14_inlet as _c14  # noqa: E402
import jg_bulkhead_union as _jg  # noqa: E402
from docgen import substitute_md  # noqa: E402

# What the row's hardware takes on the wall face, off each fitting's own panel footprint.
PORT_NUT_D, _ = _jg.panel_footprint()                        # JG bulkhead nut, across the face
PORT_C14_FLANGE_W, _ = _c14.panel_footprint()                # and the C14's bezel
# Clear wall between two adjacent nuts. A hand has to get a socket onto each one after its
# neighbour is made up, and this is the margin that leaves — the figure `_port_chain` prices a
# row of them at. `front_half.PANEL_X` stands the umbilical's three further apart than this.
PORT_NUT_GAP = 7.0


def _port_chain(n):
    """The panel width n adjacent bulkhead nuts occupy, margins included."""
    return n * PORT_NUT_D + (n - 1) * PORT_NUT_GAP


def main():
    # The row as PLACED, read off each union's own inboard collet — the same station
    # `front_half.back_wall_ports` strikes its bore on, so prose and hole cannot land on two
    # different columns.
    _pack = _fh.build_pack()
    _mouth = lambda carry: carry(_jg.port(-1.0))[0]          # noqa: E731
    _water_x = _mouth(_pack.bulkhead_carry)[0]
    _row_z = _mouth(_pack.panel_carries["bulkhead-carb"])[2]
    _umbilical = " / ".join(
        f"{_mouth(_pack.panel_carries[n])[0]:.4g}"
        for n in ("bulkhead-flavor-b", "bulkhead-flavor-a", "bulkhead-carb"))
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
        "PORT_NUT_D": f"{PORT_NUT_D:.4g}",
        "C14_FLANGE_W": f"{PORT_C14_FLANGE_W:.4g}",
        "PORT_CHAIN_4": f"{_port_chain(4):.4g}",
        "PORT_CHAIN_3": f"{_port_chain(3):.4g}",
        "PORT_ROW_Z": f"{_row_z:.4g}",
        "WATER_BACK_X": f"{_water_x:.4g}",
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
