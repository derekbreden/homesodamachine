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

# What the plate states. `nameplate.py` letters these and the README quotes them, so the plaque
# a customer reads and the page describing it carry one set of strings.
input_rating = "120V 60Hz 5A 600W"
warning_line = "120V 60Hz ONLY"
warning_line_2 = "NOT FOR 240V"
portal_host = "homesodamachine.com"


def serial_of(unit: int) -> str:
    """One unit's serial — the number, as it is lettered on the plate and as `logs/<serial>/`
    is named."""
    return f"{unit:04d}"


def unit_url(unit: int) -> str:
    """The unit's own page."""
    return f"https://{portal_host}/u/{serial_of(unit)}"


def unit_url_lines(unit: int) -> tuple:
    """That URL as the plate sets it: the host, and the path under it."""
    return (portal_host, f"/u/{serial_of(unit)}")


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
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
