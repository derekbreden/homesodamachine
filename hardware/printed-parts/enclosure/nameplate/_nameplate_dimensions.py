"""Nameplate dimensions — design constants for the rear-panel nameplate
README. No CAD geometry yet (the parametric generator is planned but
unwritten); this module exists only to source-of-truth the small set of
design numbers that appear in README.md and substitute them in via
docgen. See README.md for the design intent."""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from docgen import substitute_md


# Founder Edition run size — the single most load-bearing design number
# in this part. Sets the unit-number range (1..N), the zero-padded NNN
# format width (matches N when N ≤ 999), and the boundary where
# Standard Edition would start (N+1).
founder_edition_count = 50

# Print settings — finer than the bulk enclosure parts because the
# nameplate carries small text and a QR code.
nameplate_nozzle_diameter = 0.2     # mm — nameplate print
bulk_enclosure_nozzle_diameter = 0.4  # mm — referenced for contrast, set by other enclosure parts
layer_height_min = 0.08             # mm — fine end of the layer-height window
layer_height_max = 0.12             # mm — coarse end of the layer-height window


def main():
    # FOUNDER_EDITION_COUNT is the plain integer ("50"); FOUNDER_EDITION_LAST
    # is the zero-padded last-unit number ("050"); FOUNDER_EDITION_NEXT is
    # the zero-padded first Standard-Edition unit ("051"). All three derive
    # from `founder_edition_count` so they move together.
    variables = {
        "FOUNDER_EDITION_COUNT": f"{founder_edition_count}",
        "FOUNDER_EDITION_LAST": f"{founder_edition_count:03d}",
        "FOUNDER_EDITION_NEXT": f"{founder_edition_count + 1:03d}",
        "NAMEPLATE_NOZZLE_D": f"{nameplate_nozzle_diameter:g} mm",
        "BULK_NOZZLE_D": f"{bulk_enclosure_nozzle_diameter:g} mm",
        "LAYER_H_MIN": f"{layer_height_min:g}",
        "LAYER_H_MAX": f"{layer_height_max:g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "FOUNDER_EDITION_COUNT": 3,
            "FOUNDER_EDITION_LAST": 3,
            "FOUNDER_EDITION_NEXT": 1,
            "NAMEPLATE_NOZZLE_D": 1,
            "BULK_NOZZLE_D": 1,
            "LAYER_H_MIN": 1,
            "LAYER_H_MAX": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
