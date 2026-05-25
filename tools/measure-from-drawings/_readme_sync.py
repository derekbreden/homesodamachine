"""Variable substitution for measure-from-drawings/README.md.

The README cites two standards-based calibration nominals as canonical
references (§5.2 "Picking the calibration reference" and §6.3
"Cross-checking"):

- 1/4" tube OD nominal = 6.35 mm (= 0.25 in × 25.4).
- G 1/2 BSPP thread major nominal = 20.955 mm.

These numbers are load-bearing in the worked examples — a user calibrating
a pixel measurement against the README's recommended reference will copy
the number verbatim into their own derivation. If the README drifts (e.g.
someone "rounds" 20.955 to 20.96), the user's calibration drifts with it.
So they get tied to constants here.

The rest of the worked examples (e.g. the JG union dimensions: 41.80,
15.10, 9.31, 9.57, 14.96, 39.13; the PP1208E drawing-derived 20.96; the
Uncertainties-section 50.0/49.5/9.50) are illustrative numbers drawn from
`hardware/off-the-shelf-parts/john-guest-union/extracted-results/
geometry-description.md` or from synthetic examples. They are documented
only as markdown — there is no Python source-of-truth module to import.
The README already cross-references the JG doc by path in §9, so a
reader who wants the canonical values has a one-hop link. They stay raw.

Run as a script to substitute the README:

    tools/cad-venv/bin/python _readme_sync.py
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
