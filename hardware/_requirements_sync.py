"""Doc-sync driver for hardware/requirements.md.

Run: tools/cad-venv/bin/python hardware/_requirements_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md


# ─── Top-level design requirements ────────────────────────────────────

flavor_count = 2                # Independent flavor channels.
design_life_yr = 10             # Unmaintained appliance design life, years.


def main():
    variables = {
        "FLAVOR_COUNT": f"{flavor_count:.4g}",
        "DESIGN_LIFE_YR": f"{design_life_yr:.4g}",
        "DESIGN_LIFE_LABEL": f"{design_life_yr:.4g}-year",
    }

    substitute_md(
        _here / "requirements.md",
        variables=variables,
        expected_counts={
            "FLAVOR_COUNT": 2,
            "DESIGN_LIFE_YR": 1,
            "DESIGN_LIFE_LABEL": 1,
        },
    )
    print("-> requirements.md")


if __name__ == "__main__":
    main()
