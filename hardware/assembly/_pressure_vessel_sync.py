"""Doc-sync driver for hardware/assembly/pressure-vessel.md.

Run: tools/cad-venv/bin/python hardware/assembly/_pressure_vessel_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "cadlib"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "cold-core"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _cold_core_interface import (
    above_tank_elbows_height,
    below_tank_elbows_height,
    tank_height,
)
from docgen import substitute_md


def main():
    # The two elbow envelopes are equal by design; ELBOW_ENV is a single
    # substitution. If they diverge, split into ABOVE / BELOW variables.
    assert above_tank_elbows_height == below_tank_elbows_height, (
        f"above ({above_tank_elbows_height}) != below ({below_tank_elbows_height}); "
        "split ELBOW_ENV into ABOVE / BELOW variables."
    )

    variables = {
        # Tube cut length / tank-as-assembled height.
        "TANK_H": f"{tank_height:.4g} mm",
        # Vertical envelope for the 1/4" NPT 90° elbow stack above and
        # below the tank (foam-shell budget).
        "ELBOW_ENV": f"{above_tank_elbows_height:.4g} mm",
    }

    substitute_md(
        _here / "pressure-vessel.md",
        variables=variables,
        expected_counts={
            "TANK_H": 1,
            "ELBOW_ENV": 2,
        },
    )
    print("-> pressure-vessel.md")


if __name__ == "__main__":
    main()
