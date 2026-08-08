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
    above_tank_elbows_height,
    below_tank_elbows_height,
    tank_height,
)
from endcap_circular_dxf import disc_thickness, register_depth
from docgen import substitute_md

MM_PER_IN = 25.4

# The vessel's working pressure, and the only thing that sets it: the in-appliance
# Interstate Pneumatics WR1110 fixed secondary regulator standing between the
# customer's CGA-320 primary and the vessel's CO2 port (bom.md §4). Every pressure
# figure this procedure is sized against — the PRV margin, the hoop stress, the
# hydro hold — is measured off this one number, and the benches downstream read it
# from here: `_acceptance_and_burn_in_sync` centres its CO2 rig on it and
# `cards/_cards_fs` holds that rig's primary range around it.
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
    tank_height
    - 2 * plate_recess
    - 2 * disc_thickness * MM_PER_IN
    + 2 * register_depth * MM_PER_IN
    - rod_clearance
)


def main():
    # The two elbow envelopes are equal by design; ELBOW_ENV is a single
    # substitution. If they diverge, split into ABOVE / BELOW variables.
    assert above_tank_elbows_height == below_tank_elbows_height, (
        f"above ({above_tank_elbows_height}) != below ({below_tank_elbows_height}); "
        "split ELBOW_ENV into ABOVE / BELOW variables."
    )

    variables = {
        # Tube cut length / tank-as-assembled height.
        "TANK_H": f"{tank_height:.4g} mm",
        # Vertical envelope for the 1/4" NPT 90° elbow stack above and
        # below the tank (foam-shell budget).
        "ELBOW_ENV": f"{above_tank_elbows_height:.4g} mm",
        # Carbonator float-rod cut length (computed above).
        "ROD_LEN": f"{carbonator_rod_len:.4g} mm ({carbonator_rod_len / MM_PER_IN:.3g} in)",
        # The working pressure the whole procedure is sized against, and the
        # regulator that holds it there — one number, read everywhere it is stated.
        "WORKING_PSI": f"{secondary_regulator_pressure_psi:.4g} PSI",
        "REG_FIXED": f"fixed-{secondary_regulator_pressure_psi:.4g} PSI",
    }

    substitute_md(
        _here / "pressure-vessel.md",
        variables=variables,
        expected_counts={
            "TANK_H": 1,
            "ELBOW_ENV": 2,
            "ROD_LEN": 2,
            "WORKING_PSI": 8,
            "REG_FIXED": 1,
        },
    )
    print("-> pressure-vessel.md")


if __name__ == "__main__":
    main()
