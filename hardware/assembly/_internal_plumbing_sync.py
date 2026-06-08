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
        / "cold-core"
        / "foam-cap"
    ),
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

import foam_cap as foam_cap_gen  # noqa: E402

from docgen import substitute_md  # noqa: E402


def main():
    variables = {
        # Foam-cap CO2 inlet coordinate (Y, in cold-core foam-shell
        # coordinates) and the tube-clearance hole diameter for 1/4" OD
        # LLDPE through cap + lid. Source: `co2_inlet_y` and
        # `2 × co2_tube_clearance_radius` in foam-cap/foam_cap.py.
        "COTWO_INLET_Y": f"{foam_cap_gen.co2_inlet_y:.4g} mm",
        "COTWO_TUBE_D": f"{2 * foam_cap_gen.co2_tube_clearance_radius:.4g} mm",
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
