#!/usr/bin/env python3
"""Doc-sync driver for pie-in-the-sky/lite/assembly.md.

Pins the bag-hanger rod cut length quoted in the Lite assembly procedure to
its computed source-of-truth value — `rod_length` in reservoir_pockets.py,
the same constant that feeds the reservoir-pockets README. Keeps assembly.md
from drifting off the CAD-computed cut length.

Run:  tools/cad-venv/bin/python pie-in-the-sky/lite/_assembly_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here / "printed-parts" / "reservoir-pockets"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

import reservoir_pockets  # noqa: E402

from docgen import substitute_md  # noqa: E402


def main():
    variables = {
        # Bag-hanger rod cut length — same value pinned in the
        # reservoir-pockets README; computed in reservoir_pockets.py.
        "ROD_LENGTH": f"{reservoir_pockets.rod_length:.4g} mm",
    }

    substitute_md(
        _here / "assembly.md",
        variables=variables,
        expected_counts={"ROD_LENGTH": 2},
    )
    print("-> assembly.md")


if __name__ == "__main__":
    main()
