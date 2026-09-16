"""Doc-sync driver for hardware/assembly/pressure-vessel.md.

Run: tools/cad-venv/bin/python hardware/assembly/_pressure_vessel_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "cadlib"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "cold-core"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")
        / "cut-parts" / "carbonation" / "endcaps-circular"),
)

from _cold_core_interface import (
    above_carbonator_elbows_height,
    below_carbonator_elbows_height,
    carbonator_height,
)
from endcap_circular_dxf import disc_thickness, hole_diameter, register_depth
from docgen import substitute_md

MM_PER_IN = 25.4

# Nominal gas-feed setpoint and pressure-design reference for the in-appliance WR1110.
# Refill can compress the trapped headspace above this setpoint: the downstream check
# isolates it from the regulator's relief, so this is not a maximum vessel pressure.
# The procedure's nominal figures and the downstream bench documents read this value.
secondary_regulator_pressure_psi = 90.0

# Carbonator float-rod cut length. Each 1/4" end plate is an ID-fit plug
# RECESSED plate_recess below its tube end, so the tube wall stands proud and
# the closure is a corner fillet welded into the recess (step 3/5) — the joint
# the handheld laser runs best on a thin-wall-to-thick-plate edge. The rod's
# seat-to-seat span = tube length − both recesses − both plate thicknesses
# + both register depths (the rod tip drops register_depth into each plate).
# Cut rod_clearance under that so the rod never holds a plate off its seated
# depth (which would open the fillet root).
plate_recess = 0.25 * MM_PER_IN   # mm — plate outer face set 1/4" below the rim
rod_clearance = 1.0               # mm — cut under seat-to-seat
carbonator_rod_len = (
    carbonator_height
    - 2 * plate_recess
    - 2 * disc_thickness * MM_PER_IN
    + 2 * register_depth * MM_PER_IN
    - rod_clearance
)


def main():
    # The two elbow envelopes are equal by design; ELBOW_ENV is a single
    # substitution. If they diverge, split into ABOVE / BELOW variables.
    assert above_carbonator_elbows_height == below_carbonator_elbows_height, (
        f"above ({above_carbonator_elbows_height}) != below ({below_carbonator_elbows_height}); "
        "split ELBOW_ENV into ABOVE / BELOW variables."
    )

    variables = {
        # Tube cut length / carbonator-as-assembled height.
        "TANK_H": f"{carbonator_height:.4g} mm",
        # Vertical envelope for the 1/4" NPT 90° elbow stack above and
        # below the carbonator (foam-shell budget).
        "ELBOW_ENV": f"{above_carbonator_elbows_height:.4g} mm",
        # Carbonator float-rod cut length (computed above), and the one term of its
        # formula the prose spells out — the undercut that keeps the rod from holding
        # a plate off its seated depth. Read off the constant the length is cut with,
        # so the sentence explaining the cut cannot describe a different cut.
        "ROD_LEN": f"{carbonator_rod_len:.4g} mm ({carbonator_rod_len / MM_PER_IN:.3g} in)",
        "ROD_CLEARANCE": f"{rod_clearance:.4g} mm",
        # Nominal gas-feed setpoint / design reference, not an upper pressure bound.
        "WORKING_PSI": f"{secondary_regulator_pressure_psi:.4g} PSI",
        "REG_FIXED": f"fixed-{secondary_regulator_pressure_psi:.4g} PSI",
        # The endplate's laser-cut tap-drill opening; not the purchased elbow's flow bore.
        "PORT_BORE": f'⌀{hole_diameter * MM_PER_IN:.4g} mm ({hole_diameter:.3f}")',
    }

    substitute_md(
        _here / "pressure-vessel.md",
        variables=variables,
    )
    print("-> pressure-vessel.md")


if __name__ == "__main__":
    main()
