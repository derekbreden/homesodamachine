"""Doc-sync driver for hardware/assembly/handwork.md.

Pins the two cut-to-length float rods quoted in the skilled-hand summary to
their computed source-of-truth lengths: the carbonator float rod (shared with
pressure-vessel.md, computed in _pressure_vessel_sync.py) and the
flavor-reservoir float rods (shared with the reservoir's level-sensing.md,
computed in reservoir.py). Keeps handwork.md from drifting off the CAD-computed
cut lengths the way the old hand-typed "~6 in" carbonator length did.

Run: tools/cad-venv/bin/python hardware/assembly/_handwork_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))  # _pressure_vessel_sync (same dir)
sys.path.insert(
    0,
    str(
        next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts"
        / "cold-core"
        / "reservoir"
    ),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _pressure_vessel_sync import carbonator_rod_len  # noqa: E402
import reservoir  # noqa: E402

from docgen import substitute_md  # noqa: E402

MM_PER_IN = 25.4


def main():
    variables = {
        # Carbonator float-rod cut length — same value pinned in
        # pressure-vessel.md; computed in _pressure_vessel_sync.py.
        "ROD_LEN": (
            f"{carbonator_rod_len:.4g} mm ({carbonator_rod_len / MM_PER_IN:.3g} in)"
        ),
        # Flavor-reservoir float-rod cut length — same value pinned in the
        # reservoir's level-sensing.md; computed in reservoir.py.
        "RESERVOIR_ROD_LEN": (
            f"{reservoir.reservoir_rod_len:.4g} mm "
            f"({reservoir.reservoir_rod_len / MM_PER_IN:.3g} in)"
        ),
    }

    substitute_md(
        _here / "handwork.md",
        variables=variables,
        expected_counts={
            "ROD_LEN": 1,
            "RESERVOIR_ROD_LEN": 1,
        },
    )
    print("-> handwork.md")


if __name__ == "__main__":
    main()
