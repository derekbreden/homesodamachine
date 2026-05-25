"""Pressure-vessel.md value sync — pulls the CAD-driven dimensions cited
in the procedure prose from `_cold_core_interface.py` (the canonical
source for the vessel-as-installed envelope in the cold-core stack) and
substitutes them into pressure-vessel.md.

Only the two dimensions that the cold-core CAD owns get substituted:

- `tank_height` (the cut-to-length tube spec, also the foam-shell's
  budgeted inner-cylinder height).
- `above_tank_elbows_height` / `below_tank_elbows_height` (the vertical
  envelope reserved for the 1/4" NPT 90° elbow stack above and below
  the tank — sized by the foam-shell, referenced in the assembly prose).

Every other number in pressure-vessel.md is external (NPT thread specs,
PSI setpoints, weld recipe parameters, vendor data-sheet numbers) and
intentionally stays raw — the cold-core CAD doesn't own those, and the
assembly procedure is the source-of-truth.

Run as a script to substitute:

    tools/cad-venv/bin/python _pressure_vessel_sync.py
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
    # The two elbow envelopes are equal by design (the foam-shell budgets
    # the same 30 mm above and below the tank). Assert that here so the
    # single ELBOW_ENV substitution stays valid; if they ever diverge,
    # this script needs two separate variables.
    assert above_tank_elbows_height == below_tank_elbows_height, (
        f"above ({above_tank_elbows_height}) != below ({below_tank_elbows_height}); "
        "split ELBOW_ENV into ABOVE / BELOW variables."
    )

    variables = {
        # 152.4 mm — tube cut length, also the tank-as-assembled height.
        "TANK_H": f"{tank_height:g} mm",
        # 30 mm — the vertical envelope reserved for the 1/4" NPT 90°
        # elbow stack above and below the tank (foam-shell budget).
        "ELBOW_ENV": f"{above_tank_elbows_height:g} mm",
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
