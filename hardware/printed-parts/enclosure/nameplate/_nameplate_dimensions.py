"""Doc-sync driver for hardware/printed-parts/enclosure/nameplate/README.md.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from docgen import substitute_md


# Founder Edition run size: units 1..N.
founder_edition_count = 50

# Print settings for the small text and QR code the nameplate carries.
nameplate_nozzle_diameter = 0.2     # mm
bulk_enclosure_nozzle_diameter = 0.4  # mm — owned by other enclosure parts
layer_height_min = 0.08             # mm
layer_height_max = 0.12             # mm


def main():
    variables = {
        "FOUNDER_EDITION_COUNT": f"{founder_edition_count}",
        "FOUNDER_EDITION_LAST": f"{founder_edition_count:03d}",
        "FOUNDER_EDITION_NEXT": f"{founder_edition_count + 1:03d}",
        "NAMEPLATE_NOZZLE_D": f"{nameplate_nozzle_diameter:.4g} mm",
        "BULK_NOZZLE_D": f"{bulk_enclosure_nozzle_diameter:.4g} mm",
        "LAYER_H_MIN": f"{layer_height_min:.4g}",
        "LAYER_H_MAX": f"{layer_height_max:.4g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "FOUNDER_EDITION_COUNT": 2,
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
