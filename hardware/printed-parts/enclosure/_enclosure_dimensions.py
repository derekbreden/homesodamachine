"""Doc-sync driver for hardware/printed-parts/enclosure/README.md and
the source of truth for the enclosure outer dimensions imported by the
isometric drawings.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/_enclosure_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cold-core"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cold_core_interface import (
    foam_shell_outer_height,
    outer_shell_x_length,
    outer_shell_y_length,
)
from docgen import substitute_md


# Foam shell occupies Zone A entirely. The enclosure follows the foam
# shell's footprint at the back.
APPLIANCE_W = outer_shell_x_length

# Zone D (front-bottom) lives in front of the foam shell; the condenser is
# its deepest item. The rear service plenum (mirrors
# enclosure-assembly/_contents.py PLENUM_DEPTH) sits behind the shell.
# Together the three strata drive the appliance depth.
CONDENSER_DEPTH = 150.0
REAR_PLENUM_DEPTH = 30.0
APPLIANCE_D = outer_shell_y_length + CONDENSER_DEPTH + REAR_PLENUM_DEPTH


def main():
    variables = {
        "FOAM_SHELL_X": f"{outer_shell_x_length:.4g}",
        "FOAM_SHELL_Y": f"{outer_shell_y_length:.4g}",
        "FOAM_SHELL_Z": f"{foam_shell_outer_height:.4g}",
        "APPLIANCE_WIDTH": f"{APPLIANCE_W:.4g} mm",
        "APPLIANCE_DEPTH": f"{APPLIANCE_D:.4g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "FOAM_SHELL_X": 1,
            "FOAM_SHELL_Y": 1,
            "FOAM_SHELL_Z": 1,
            "APPLIANCE_WIDTH": 1,
            "APPLIANCE_DEPTH": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
