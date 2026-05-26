"""Doc-sync driver for hardware/printed-parts/enclosure/front-panel/README.md.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/front-panel/_front_panel_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from docgen import substitute_md


# ESP32-S3 detach cord length.
display_detach_cord_length_m = 1.0

# UART + 5 V supply over the detach cord.
display_detach_signal_voltage = 5.0

# CGA-320 primary regulator hose length (BOM §4).
cga_short_tether_length_inches = 12.0

# WR1110 fixed secondary regulator setpoint.
secondary_regulator_pressure_psi = 90.0


def main():
    variables = {
        "DISPLAY_CORD_L": f"~{display_detach_cord_length_m:.4g} m",
        "DISPLAY_SIGNAL_V": f"{display_detach_signal_voltage:.4g} V",
        "CGA_TETHER_L": f'~{cga_short_tether_length_inches:.4g}"',
        "REGULATOR_PRESSURE": f"fixed-{secondary_regulator_pressure_psi:.4g} PSI",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "DISPLAY_CORD_L": 2,
            "DISPLAY_SIGNAL_V": 1,
            "CGA_TETHER_L": 1,
            "REGULATOR_PRESSURE": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
