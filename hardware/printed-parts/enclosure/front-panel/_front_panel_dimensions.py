"""Front-panel dimensions — the named constants that the README's prose
refers to. No CAD geometry yet (this part is still design-in-progress);
this module is the source-of-truth for the dimensional numbers cited in
README.md until the panel reaches a CAD generator.

Run this module directly to substitute the values into README.md."""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from docgen import substitute_md


# ESP32-S3 rotary display detach mechanism. The display sits in a recess
# on the front face; the customer pulls it out and the cord behind the
# panel pays out so they can hold the display or mount it on the cabinet's
# false-drawer-front. Cord length is the working slack budget — enough to
# reach the false-drawer-front from the recess seat with margin for hand
# manipulation. Used in two places: the front-features table row and the
# §"S3 detach mechanism" detail section.
display_detach_cord_length_m = 1.0

# UART + 5 V supply over the detach cord (Cat6 candidate per the
# §"S3 detach mechanism" open candidates). The 5 V rail is what the
# ESP32-S3 module wants; the cord spec follows from it.
display_detach_signal_voltage = 5.0

# Customer's CGA-320 primary regulator hose ("short tether") — the
# red 5/16" beer-line PVC run from the cylinder valve to the front-panel
# DERPIPE inlet. Length is the "obvious path from the cylinder around
# the front-side corner to the inlet" envelope; sourced via BOM §4.
cga_short_tether_length_inches = 12.0

# WR1110 fixed secondary regulator — pressure setpoint downstream of
# the front-panel inlet stack (GASHER check → WR1110 → PTC adapter →
# foam-cap top). Sets the vessel-side CO2 supply pressure.
secondary_regulator_pressure_psi = 90.0

# CO2 cylinder filled weight — used in the cylinder-placement rationale
# ("not in front of the front face" / "pressurized aluminum bottle in the
# customer's shins"). Typical 5-lb aluminum CO2 cylinder weighs ~9 lb
# filled (tare + 5 lb gas), so this is the worst-case shin-impact mass
# that motivates the side-gap placement.
co_cylinder_filled_weight_lb = 9.0


def main():
    # Variable names are uppercase letters + underscores only — the docgen
    # regex `[A-Z_]+` does not match digits, so e.g. CO2 must spell out as
    # CO (the prose around the reference still says "CO2"; the variable
    # name is purely an identifier in the markdown link's href position).
    variables = {
        # Display detach mechanism.
        "DISPLAY_CORD_L": f"~{display_detach_cord_length_m:g} m",
        "DISPLAY_SIGNAL_V": f"{display_detach_signal_voltage:g} V",
        # CO2 inlet stack — design-rationale numbers.
        "CGA_TETHER_L": f'~{cga_short_tether_length_inches:g}"',
        "REGULATOR_PRESSURE": f"fixed-{secondary_regulator_pressure_psi:g} PSI",
        "CYLINDER_WEIGHT": f"~{co_cylinder_filled_weight_lb:g} lb",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "DISPLAY_CORD_L": 2,
            "DISPLAY_SIGNAL_V": 1,
            "CGA_TETHER_L": 1,
            "REGULATOR_PRESSURE": 1,
            "CYLINDER_WEIGHT": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
