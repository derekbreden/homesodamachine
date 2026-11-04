"""Doc-sync driver for hardware/printed-parts/enclosure/nameplate/README.md.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
sys.path.insert(0, str(_root / "tools"))

from docgen import substitute_md

sys.path.insert(0, str(_root / "hardware/printed-parts/enclosure/enclosure"))
from _enclosure_data import dimensions as _dimensions, read as _read


globals().update(_dimensions()['plan'])


def serial_of(unit: int) -> str:
    """The four-digit identifier encoded in the QR and used by the unit log."""
    return _read('nameplate-unit', unit=unit, portal_host=portal_host)['serial']


def unit_url(unit: int) -> str:
    """Uppercase scheme/host keep the complete URL in QR alphanumeric mode."""
    return _read('nameplate-unit', unit=unit, portal_host=portal_host)['url']


def unit_url_plain(unit: int) -> str:
    """The full-domain address for written instructions; the plate shows only a QR."""
    return _read('nameplate-unit', unit=unit, portal_host=portal_host)['plain']


def main():
    variables = _read('plan-variables', plan=_dimensions()['plan'])

    substitute_md(
        _here / "README.md",
        variables=variables,
    )
    print("-> README.md")
    substitute_md(_root / "future" / "unit-links.md", variables=variables)
    print("-> future/unit-links.md")


if __name__ == "__main__":
    main()
