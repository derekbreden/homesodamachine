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
from docgen import substitute_md

import importlib.util


def _load_module(name: str, file_path: Path):
    """Load a Python file as a uniquely-named module."""
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(file_path.parent))
    spec.loader.exec_module(module)
    return module


# Coil tie-in tail length — owned by the coil-mandrel generator alongside
# the wrap arc it extends.
_coil_mandrel_gen = _load_module(
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

# ─── Recharge target + metering tolerance ────────────────────────────

system_charge_approx_g = 40             # rough per-system R-600a usage
recharge_tolerance_g = 1                # ±, mass-meter precision target
volume_correction_low_g = 5             # +, factory-mass to recharge
volume_correction_high_g = 15           # +, factory-mass to recharge
evap_volume_delta_low_ml = 80           # vs factory finger-plate
evap_volume_delta_high_ml = 110         # vs factory finger-plate

# ─── Vacuum spec ──────────────────────────────────────────────────────
# Orion Motor Tech 4 CFM single-stage pump (150 µ ultimate).

vacuum_target_microns = 500             # ≤, pre-charge vacuum target
vacuum_hold_minutes = 15                # min hold + isolation hold each

# ─── First run-up expectations ────────────────────────────────────────

compressor_running_current_a = 1        # ~, first run-up steady state
compressor_off_time_min = 3             # firmware-enforced minimum

# ─── Safety distances ────────────────────────────────────────────────

vent_ignition_clearance_m = 3           # min distance to any ignition source

# ─── Hardware backstop spec (SF76E thermal fuse) ──────────────────────

sf76e_open_temp_c = 77                  # BOJACK SF76E SEFUSE open temp


def main():
    variables = {
        # Factory charge masses.
        "UNIT_A_CHARGE": f"{unit_a_factory_charge_g:.4g} g",
        "UNIT_B_CHARGE": f"{unit_b_factory_charge_g:.4g} g",
        # Recharge target + metering tolerance.
        "SYSTEM_CHARGE": f"~{system_charge_approx_g:.4g} g",
        "RECHARGE_TOL": f"±{recharge_tolerance_g:.4g} g",
        "VOL_CORRECTION": (
            f"+{volume_correction_low_g:.4g}-{volume_correction_high_g:.4g} g"
        ),
        "EVAP_VOL_DELTA": (
            f"~{evap_volume_delta_low_ml:.4g}-{evap_volume_delta_high_ml:.4g} mL"
        ),
        # Vacuum spec.
        "VACUUM_TARGET": f"{vacuum_target_microns:.4g} microns",
        "VACUUM_HOLD": f"{vacuum_hold_minutes:.4g} min",
        "VACUUM_HOLD_FULL": f"{vacuum_hold_minutes:.4g} minutes",
        # First run-up.
        "RUN_CURRENT": f"~{compressor_running_current_a:.4g} A",
        "OFF_TIME": f"{compressor_off_time_min:.4g}-minute",
        # Safety distance.
        "VENT_CLEARANCE": f"{vent_ignition_clearance_m:.4g} m",
        # SF76E thermal fuse.
        "SF76E_TEMP": f"{sf76e_open_temp_c:.4g} °C",
        # Coil tie-in tail (coil_mandrel.py).
        "STUB_LEN": f"{_coil_mandrel_gen.stub_allowance:.4g} mm",
    }

    substitute_md(
        _here / "refrigerant-loop.md",
        variables=variables,
        expected_counts={
            "UNIT_A_CHARGE": 3,
            "UNIT_B_CHARGE": 3,
            "SYSTEM_CHARGE": 1,
            "RECHARGE_TOL": 3,
            "VOL_CORRECTION": 1,
            "EVAP_VOL_DELTA": 1,
            "VACUUM_TARGET": 2,
            "VACUUM_HOLD": 1,
            "VACUUM_HOLD_FULL": 2,
            "RUN_CURRENT": 1,
            "OFF_TIME": 1,
            "VENT_CLEARANCE": 1,
            "SF76E_TEMP": 2,
            "STUB_LEN": 2,
        },
    )
    print("-> refrigerant-loop.md")


if __name__ == "__main__":
    main()
