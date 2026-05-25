"""Foam shell — the PETG enclosure for the cold core's pressure
vessel + copper evaporator coil + flavor reservoir pockets. See
README.md for the design intent and the layer-by-layer geometry.
(Previously named foam-bag-shell when the reservoirs were flexible
bags; renamed to foam-shell when the design moved to printed PETG
reservoirs.)"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cadq_export import export_step
from _foam_shell import build_full_shell
from _cold_core_interface import (
    foam_shell_outer_height,
    outer_shell_foam_gap,
    outer_shell_x_length,
    outer_shell_z_length,
)
from docgen import substitute_md


def main():
    foam_shell = build_full_shell()
    export_step(foam_shell, str(_here / "foam-shell.step"))
    print("-> foam-shell.step")

    substitute_md(
        _here / "README.md",
        variables={
            "FOAM_SHELL_OUTER_HEIGHT": f"{foam_shell_outer_height:g}",
            "OUTER_SHELL_FOAM_GAP": f"{outer_shell_foam_gap:g}",
            "OUTER_SHELL_X_LENGTH": f"{outer_shell_x_length:g}",
            "OUTER_SHELL_Z_LENGTH": f"{outer_shell_z_length:g}",
        },
        expected_counts={
            "FOAM_SHELL_OUTER_HEIGHT": 2,
            "OUTER_SHELL_FOAM_GAP": 2,
            "OUTER_SHELL_X_LENGTH": 1,
            "OUTER_SHELL_Z_LENGTH": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
