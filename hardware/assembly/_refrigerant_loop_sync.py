"""Procedure-parameter sync for hardware/assembly/refrigerant-loop.md.

No geometry generator — this module exists as the source of truth for
numerics in the refrigerant-loop production procedure (factory charge
masses, recharge tolerance, vacuum target, hold times, first-run-up
expectations, leak-detection backstop spec, etc.). The README's
[value](NAME) markers substitute against these constants so prose
and numbers stay in sync as the procedure is tuned.

R-600a thermodynamic properties (LFL ~1.8 %), refrigerant class names
(R-134a, R-410a), and commercial part specs (BCuP-5 15 % Ag, 0.031"
capillary tube, etc.) are deliberately left raw — they are industry-
standard data or vendor catalog numbers, not procedure parameters.

Factory charge masses for the two tracked donors are documented at
their authoritative source in
hardware/harvested/ice-maker/README.md "Unit A" / "Unit B". The
values mirrored here are kept synchronized with that doc.

Run as a script to substitute the README:

    tools/cad-venv/bin/python _refrigerant_loop_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md


# ─── Factory charge masses (per harvested/ice-maker/README.md) ────────
# Mirrored from authoritative source in harvested README, where each
# value is sourced to the donor's manufacturer manual.

unit_a_factory_charge_g = 15            # Antarctic Star HZB-12/Q manual
unit_b_factory_charge_g = 23            # Frigidaire EFIC117-SS manual

# ─── Recharge target + metering tolerance ────────────────────────────
# The recharge target for this build is *not* the factory mass because
# the new evaporator coil has greater internal volume than the
# discarded factory finger-plate; see Open items §1 in the README.

system_charge_approx_g = 40             # rough per-system R-600a usage
recharge_tolerance_g = 1                # ±, mass-meter precision target
volume_correction_low_g = 5             # +, factory-mass to recharge
volume_correction_high_g = 15           # +, factory-mass to recharge
evap_volume_delta_low_ml = 80           # vs factory finger-plate
evap_volume_delta_high_ml = 110         # vs factory finger-plate

# ─── Vacuum spec ──────────────────────────────────────────────────────
# Pulled down with Orion Motor Tech 4 CFM single-stage pump (150 µ
# ultimate) — vacuum target sits comfortably above the pump's ultimate.

vacuum_target_microns = 500             # ≤, pre-charge vacuum target
vacuum_hold_minutes = 15                # min hold + isolation hold each

# ─── First run-up expectations ────────────────────────────────────────
# Compressor electrical signature on first energize. 1 A running
# current is the donor compressor's expected steady-state draw; the
# 3-minute minimum off-time is the firmware-enforced hermetic-restart
# guard documented in harvested/ice-maker/README.md "Powering and control".

compressor_running_current_a = 1        # ~, first run-up steady state
compressor_off_time_min = 3             # firmware-enforced minimum

# ─── Safety distances ────────────────────────────────────────────────
# Per-vent clearance during factory-charge release at the BPV31.

vent_ignition_clearance_m = 3           # min distance to any ignition source

# ─── Hardware backstop spec (SF76E thermal fuse) ──────────────────────
# Single-shot SEFUSE in series with the AC primary feeding the
# compressor, inside the compressor shroud. Hardware backstop to the
# firmware overtemp cutoff. Full backstop architecture lives in the
# compressor-shroud README; only the fuse temperature appears here.

sf76e_open_temp_c = 77                  # BOJACK SF76E SEFUSE open temp


def main():
    variables = {
        # Factory charge masses.
        "UNIT_A_CHARGE": f"{unit_a_factory_charge_g:g} g",
        "UNIT_B_CHARGE": f"{unit_b_factory_charge_g:g} g",
        # Recharge target + metering tolerance.
        "SYSTEM_CHARGE": f"~{system_charge_approx_g:g} g",
        "RECHARGE_TOL": f"±{recharge_tolerance_g:g} g",
        "VOL_CORRECTION": (
            f"+{volume_correction_low_g:g}-{volume_correction_high_g:g} g"
        ),
        "EVAP_VOL_DELTA": (
            f"~{evap_volume_delta_low_ml:g}-{evap_volume_delta_high_ml:g} mL"
        ),
        # Vacuum spec.
        "VACUUM_TARGET": f"{vacuum_target_microns:g} microns",
        "VACUUM_HOLD": f"{vacuum_hold_minutes:g} min",
        "VACUUM_HOLD_FULL": f"{vacuum_hold_minutes:g} minutes",
        # First run-up.
        "RUN_CURRENT": f"~{compressor_running_current_a:g} A",
        "OFF_TIME": f"{compressor_off_time_min:g}-minute",
        # Safety distance.
        "VENT_CLEARANCE": f"{vent_ignition_clearance_m:g} m",
        # SF76E thermal fuse.
        "SF76E_TEMP": f"{sf76e_open_temp_c:g} °C",
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
        },
    )
    print("-> refrigerant-loop.md")


if __name__ == "__main__":
    main()
