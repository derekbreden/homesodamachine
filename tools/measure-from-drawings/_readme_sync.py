"""Doc-sync driver for tools/measure-from-drawings/README.md.

Run: tools/cad-venv/bin/python tools/measure-from-drawings/_readme_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md


# ─── Standards-based calibration nominals ─────────────────────────────
# Source: ISO 228-1 (G-series BSPP threads); 1/4" = 0.25 in × 25.4 mm/in.
# These are the two calibration references the README §5.2 names by
# canonical value. Keep numeric precision matching the standard:
# G 1/2 BSPP major is 20.955 mm (3 decimals); 1/4" → 6.35 mm (2 decimals).

quarter_inch_tube_od_mm = 0.25 * 25.4    # = 6.35 mm, 1/4" nominal tube OD
g_half_bspp_major_mm = 20.955            # G 1/2 BSPP nominal major OD


def main() -> None:
    variables = {
        "QUARTER_INCH_MM": f"{quarter_inch_tube_od_mm:g} mm",
        "G_HALF_MAJOR_MM": f"{g_half_bspp_major_mm:g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "QUARTER_INCH_MM": 2,
            "G_HALF_MAJOR_MM": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
