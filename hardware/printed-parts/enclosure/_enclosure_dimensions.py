"""Top-level enclosure dimensions — the named constants that the
enclosure README's prose refers to. No CAD geometry at this level
(the enclosure-as-a-whole is an architectural orientation rather than
a single printed part); this module is the source-of-truth for the
dimensional numbers cited in README.md.

The foam shell envelope numbers are pulled live from
`_cold_core_interface.py` — the canonical CAD source — so any shift
in the foam shell's outer dimensions propagates here on the next run.

Run this module directly to substitute the values into README.md."""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cold-core"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cold_core_interface import (
    foam_shell_outer_height,
    outer_shell_x_length,
    outer_shell_z_length,
)
from docgen import substitute_md


def main():
    # Foam shell occupies Zone A entirely. The enclosure follows the
    # foam shell's footprint at the back, so the appliance width ≈ the
    # foam shell's X length. Pulled live from _cold_core_interface so
    # any change to the foam shell shows up in the enclosure prose.
    variables = {
        "FOAM_SHELL_X": f"{outer_shell_x_length:g}",
        "FOAM_SHELL_Z": f"{outer_shell_z_length:g}",
        "FOAM_SHELL_Y": f"{foam_shell_outer_height:g}",
        "APPLIANCE_WIDTH": f"{outer_shell_x_length:g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "FOAM_SHELL_X": 1,
            "FOAM_SHELL_Z": 1,
            "FOAM_SHELL_Y": 1,
            "APPLIANCE_WIDTH": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
