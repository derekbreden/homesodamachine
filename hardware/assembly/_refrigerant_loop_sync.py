"""Doc-sync driver for hardware/assembly/refrigerant-loop.md.

Run: tools/cad-venv/bin/python hardware/assembly/_refrigerant_loop_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import load_module, substitute_md


# Coil tie-in stubs — owned by the coil-mandrel generator alongside the wrap arc
# they extend. What this procedure sees is the PROTRUDING half of each allowance;
# the rest of it is the tail's own run inside the shell, already foamed in.
_coil_mandrel_gen = load_module(
    "refrigerant_loop_coil_mandrel_gen",
    next(p for p in _here.parents if p.name == "hardware")
    / "printed-parts"
    / "cold-core"
    / "coil-mandrel"
    / "coil_mandrel.py",
)


# ─── Factory charge masses ────────────────────────────────────────────
# Source: reference/ice-maker/README.md.

unit_a_factory_charge_g = 15            # Antarctic Star HZB-12/Q manual
unit_b_factory_charge_g = 23            # Frigidaire EFIC117-SS manual

# Project process targets. These numbers do not qualify service equipment,
# vacuum decay, the finished-unit charge or the printed plug's thermal limit.
recharge_tolerance_g = 1
vacuum_target_microns = 500
vacuum_hold_minutes = 15
compressor_running_current_a = 1        # approximate observation, not acceptance
compressor_off_time_min = 3             # firmware minimum, donor may require more
sf76e_open_temp_c = 77
petg_glass_transition_c = 80            # nominal material datum, not a safe limit
joint_standoff_mm = 92.0


def main():
    variables = {
        # Factory charge masses.
        "UNIT_A_CHARGE": f"{unit_a_factory_charge_g:.4g} g",
        "UNIT_B_CHARGE": f"{unit_b_factory_charge_g:.4g} g",
        # Recharge target + metering tolerance.
        "RECHARGE_TOL": f"±{recharge_tolerance_g:.4g} g",
        # Vacuum spec.
        "VACUUM_TARGET": f"{vacuum_target_microns:.4g} microns",
        "VACUUM_HOLD": f"{vacuum_hold_minutes:.4g} min",
        "VACUUM_HOLD_FULL": f"{vacuum_hold_minutes:.4g} minutes",
        # First run-up.
        "RUN_CURRENT": f"~{compressor_running_current_a:.4g} A",
        "OFF_TIME": f"{compressor_off_time_min:.4g}-minute",
        # SF76E thermal fuse.
        "SF76E_TEMP": f"{sf76e_open_temp_c:.4g} °C",
        # Coil tie-in stubs (coil_mandrel.py) — the PROTRUDING half of each allowance.
        "PROT_INLET": f"{_coil_mandrel_gen.stub_protrusion['inlet']:.4g} mm",
        "PROT_OUTLET": f"{_coil_mandrel_gen.stub_protrusion['outlet']:.4g} mm",
        # Brazing heat against the printed copper-plug stack.
        "PETG_TG": f"~{petg_glass_transition_c:.4g} °C",
        "JOINT_STANDOFF": f"~{joint_standoff_mm:.4g} mm",
    }

    substitute_md(
        _here / "refrigerant-loop.md",
        variables=variables,
    )
    print("-> refrigerant-loop.md")


if __name__ == "__main__":
    main()
