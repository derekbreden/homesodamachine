"""Doc-sync driver for hardware/assembly/internal-plumbing.md.

Run: tools/cad-venv/bin/python hardware/assembly/_internal_plumbing_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(
    0,
    str(
        next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts"
        / "cadlib"
    ),
)
sys.path.insert(
    0,
    str(
        next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts"
        / "cold-core"
    ),
)

from _cold_core_interface import co2_inlet_y, co2_inlet_tube_radius  # noqa: E402

from docgen import substitute_md  # noqa: E402


def main():
    variables = {
        # CO2 inlet coordinate (Y, in cold-core foam-shell coordinates) and the
        # tube-clearance hole diameter for the 1/4" OD LLDPE through the foam lid.
        # Source: `co2_inlet_y` and `2 × co2_inlet_tube_radius` in
        # _cold_core_interface.py.
        "COTWO_INLET_Y": f"{co2_inlet_y:.4g} mm",
        "COTWO_TUBE_D": f"{2 * co2_inlet_tube_radius:.4g} mm",
    }

    substitute_md(
        _here / "internal-plumbing.md",
        variables=variables,
        expected_counts={
            "COTWO_INLET_Y": 1,
            "COTWO_TUBE_D": 1,
        },
    )
    print("-> internal-plumbing.md")


if __name__ == "__main__":
    main()
