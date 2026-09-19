"""Doc-sync driver for hardware/printed-parts/enclosure/nameplate/README.md.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
sys.path.insert(0, str(_root / "tools"))

from docgen import substitute_md


# Print settings for the small text and QR code the nameplate carries.
nameplate_nozzle_diameter = 0.4     # mm, hardened nozzle for PET-GF
bulk_enclosure_nozzle_diameter = 0.4  # mm — owned by other enclosure parts
layer_height_min = 0.24             # mm
layer_height_max = 0.24             # mm

portal_host = "hosm.us"


def serial_of(unit: int) -> str:
    """The four-digit identifier encoded in the QR and used by the unit log."""
    if not isinstance(unit, int) or isinstance(unit, bool) or not 1 <= unit <= 9999:
        raise ValueError("A nameplate unit must be an integer from 1 to 9999")
    return f"{unit:04d}"


def unit_url(unit: int) -> str:
    """Uppercase scheme/host keep the complete URL in QR alphanumeric mode."""
    return f"HTTPS://{portal_host.upper()}/{serial_of(unit)}"


def unit_url_plain(unit: int) -> str:
    """The full-domain address for written instructions; the plate shows only a QR."""
    return f"homesodamachine.com/{serial_of(unit)}"


def main():
    variables = {
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
    substitute_md(_root / "future" / "unit-links.md", variables=variables)
    print("-> future/unit-links.md")


if __name__ == "__main__":
    main()
