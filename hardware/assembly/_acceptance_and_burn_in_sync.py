"""Acceptance + burn-in procedure parameters — source-of-truth constants
for the numbers cited in `acceptance-and-burn-in.md`.

No CAD geometry here; this is a procedure spec, not a part. The
constants below are factory-acceptance test parameters (setpoints to
verify, bench-rig tooling specs, pass/fail thresholds, burn-in
duration and cadence) — each one is a deliberate choice in the
acceptance procedure, and the markdown's [value](NAME) markers
substitute against them so prose and numbers stay in sync as the
procedure is tuned across early units.

One number is pulled live from upstream — the WR1110 secondary
regulator setpoint (90 PSI) — from the front-panel dimensions module
where the customer-facing inlet stack documents the same value. Every
other number is local to this procedure.

Run as a script to substitute the markdown:

    tools/cad-venv/bin/python _acceptance_and_burn_in_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "enclosure" / "front-panel"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _front_panel_dimensions import secondary_regulator_pressure_psi
from docgen import substitute_md


# ─── Firmware setpoints loaded at commissioning (verified here) ────────
# These are the setpoint values firmware should have loaded out of
# `firmware-and-commissioning.md`. Acceptance verifies the unit
# behaves to these setpoints; the values themselves come from the
# refrigeration-loop design (`refrigerant-loop.md`).
carbonator_wall_setpoint_c = 2          # carbonator wall service temperature
carbonator_wall_band_c = 2              # hysteresis band ± around setpoint
evap_coil_freeze_cutout_c = -8          # evap-coil DS18B20 freeze-protect trip
compressor_min_off_min = 3              # compressor minimum off-time before re-energize

# ─── Bench test rig — water source ─────────────────────────────────────
# Building-cold-water-tap envelope; the appliance sees this in lieu of
# the customer's under-sink supply.
bench_water_press_min_psi = 40          # bench water tap pressure, low end
bench_water_press_max_psi = 80          # bench water tap pressure, high end
bench_water_temp_max_c = 20             # bench water temperature, upper bound

# ─── Bench test rig — CO2 source ───────────────────────────────────────
# Customer-side cylinder envelope. Either size is acceptable; the
# WR1110 holds appliance-side regardless.
co2_cyl_small_lb = 5                    # small bench cylinder
co2_cyl_large_lb = 10                   # large bench cylinder
co2_primary_min_psi = 70                # primary regulator setpoint, low end
co2_primary_max_psi = 100               # primary regulator setpoint, high end

# Centerline: matches the in-appliance WR1110 secondary regulator
# setpoint, pulled live from front-panel dimensions so the centerline
# stays in lock-step with the regulator selection upstream.
co2_centerline_psi = secondary_regulator_pressure_psi

# ─── Bench test rig — measurement tooling ──────────────────────────────
glass_capacity_oz = 12                  # target dispense glass capacity
graduated_cyl_min_ml = 250              # minimum graduated-cylinder size
thermo_range_low_c = 0                  # thermometer range, low end
thermo_range_high_c = 20                # thermometer range, high end
thermo_accuracy_c = 0.5                 # thermometer accuracy spec; also doubles
                                        # as the DS18B20 first-read agreement band
refractometer_range_brix_low = 0        # refractometer range, low end
refractometer_range_brix_high = 32      # refractometer range, high end

# ─── Test-syrup consumption per unit ───────────────────────────────────
concentrate_consumed_ml_per_unit = 50   # total concentrate dispensed across acceptance
sodastream_bottle_ml = 440              # SodaStream concentrate bottle size (0.44 L)
concentrate_consumed_pct = round(
    concentrate_consumed_ml_per_unit / sodastream_bottle_ml * 100
)                                       # derived — fraction of one bottle consumed

# ─── Step 4 — CO2 leak-tight hold ──────────────────────────────────────
prv_hold_min = 2                        # PRV leak-tight observation window

# ─── Step 5 — first carbonated-water dispense ──────────────────────────
# Wall-temperature gate (operator waits until wall is at-or-below this
# before pouring) is setpoint + full hysteresis band; the compressor's
# cut-off event itself is at setpoint, but the gate runs slightly
# looser so the operator isn't blocked by 0.1 °C overshoot.
wall_disp_gate_c = carbonator_wall_setpoint_c + carbonator_wall_band_c  # derived
dispense_temp_max_c = 6                 # max dispensed-water temperature at the glass
foam_head_hold_sec = 10                 # minimum foam-head persistence before break

# ─── Step 6/7 — metered ratio test ─────────────────────────────────────
syrup_ratio_water = 20                  # ratio water:syrup numerator (water side)
syrup_ratio_syrup = 1                   # ratio water:syrup denominator (syrup side)
metered_water_ml = 250                  # metered carbonated-water dispense target
metered_flavor_ml = metered_water_ml / syrup_ratio_water  # = 12.5 — derived from ratio
metered_total_ml = metered_water_ml + metered_flavor_ml   # = 262.5 — derived
ratio_volume_tol_pct = 5                # ±% on total metered volume
metered_total_low_ml = round(metered_total_ml * (1 - ratio_volume_tol_pct / 100))   # = 250
metered_total_high_ml = round(metered_total_ml * (1 + ratio_volume_tol_pct / 100))  # = 276
channel_to_channel_tol_pct = 10         # cross-channel refractometer agreement band

# ─── Step 11 — multi-hour burn-in ──────────────────────────────────────
reservoir_burnin_fill_pct = 50          # reservoir level at burn-in start
burn_in_dispense_oz = 6                 # per-dispense volume during burn-in
burn_in_interval_min = 75               # interval between metered dispenses
burn_in_hours = 8                       # minimum sustained burn-in window
burn_in_min_dispenses = 6               # minimum metered dispenses across the window
duty_cycle_low_pct = 10                 # lower-bound of acceptable duty-cycle band
duty_cycle_high_pct = 70                # upper-bound of acceptable duty-cycle band


def main():
    variables = {
        # Firmware setpoints — § "Scope" In: row.
        "WALL_SETPOINT": f"{carbonator_wall_setpoint_c:g} °C",
        "WALL_BAND": f"± {carbonator_wall_band_c:g} °C",
        "FREEZE_CUTOUT": f"−{abs(evap_coil_freeze_cutout_c):g} °C",
        "MIN_OFF": f"{compressor_min_off_min:g} min",

        # Bench water rig.
        "WATER_PRESS_RANGE": f"{bench_water_press_min_psi:g}–{bench_water_press_max_psi:g} PSI",
        "WATER_TEMP_MAX": f"~{bench_water_temp_max_c:g} °C",
        "TAP_WATER_TEMP": f"~{bench_water_temp_max_c:g} °C",

        # Bench CO2 rig.
        "CO2_CYL_SMALL": f"{co2_cyl_small_lb:g} lb",
        "CO2_CYL_LARGE": f"{co2_cyl_large_lb:g} lb",
        "CO2_PRIMARY_RANGE": f"{co2_primary_min_psi:g}–{co2_primary_max_psi:g} PSI",
        # Centerline form ("90 PSI"). Each occurrence in the markdown
        # is in some sentence that doesn't fold neatly with the range
        # form, so the centerline gets its own variable. Sourced from
        # the front-panel WR1110 setpoint upstream — same number, same
        # ground truth.
        "CO2_CENTERLINE": f"{co2_centerline_psi:g} PSI",

        # Bench measurement tooling.
        "GLASS_OZ": f"{glass_capacity_oz:g} oz",
        "CYL_MIN": f"{graduated_cyl_min_ml:g} mL",
        "THERMO_RANGE": f"{thermo_range_low_c:g}–{thermo_range_high_c:g} °C",
        "THERMO_ACC": f"±{thermo_accuracy_c:g} °C",
        "BRIX_RANGE": f"{refractometer_range_brix_low:g}–{refractometer_range_brix_high:g} °Brix",

        # Test-syrup consumption per unit.
        "CONC_ML": f"~{concentrate_consumed_ml_per_unit:g} mL",
        "CONC_PCT": f"~{concentrate_consumed_pct:g} %",
        "BOTTLE_L": f"{sodastream_bottle_ml / 1000:.2f} L",

        # Step 4 leak hold.
        "PRV_HOLD": f"{prv_hold_min:g}-minute",

        # Step 5 first carbonated dispense.
        "WALL_DISP_GATE": f"{wall_disp_gate_c:g} °C",
        "DISP_TEMP_MAX": f"~{dispense_temp_max_c:g} °C",
        "DISP_TEMP_FAIL": f"{dispense_temp_max_c:g} °C",
        "FOAM_HOLD": f"{foam_head_hold_sec:g} seconds",

        # Step 6/7 metered ratio test.
        "RATIO": f"{syrup_ratio_syrup:g}:{syrup_ratio_water:g}",
        "METERED_WATER": f"~{metered_water_ml:g} mL",
        "METERED_FLAVOR": f"~{metered_flavor_ml:g} mL",
        "METERED_TOTAL": f"~{metered_total_ml:g} mL",
        "RATIO_TOL": f"~{ratio_volume_tol_pct:g} %",
        "RATIO_TOL_SIGNED": f"±{ratio_volume_tol_pct:g} %",
        "METERED_RANGE": f"~{metered_total_low_ml:g}–{metered_total_high_ml:g} mL",
        "CHANNEL_TOL": f"~{channel_to_channel_tol_pct:g} %",
        "CHANNEL_TOL_FAIL": f"{channel_to_channel_tol_pct:g} %",

        # Step 11 burn-in.
        "RESERVOIR_FILL_PCT": f"~{reservoir_burnin_fill_pct:g} %",
        "BURN_IN_DISP": f"~{burn_in_dispense_oz:g} oz",
        "DISP_INTERVAL": f"{burn_in_interval_min:g} minutes",
        "BURN_IN_HOURS": f"{burn_in_hours:g} hours",
        "BURN_IN_HOURS_DASH": f"{burn_in_hours:g}-hour",
        "BURN_IN_MIN_DISP": f"{burn_in_min_dispenses:g} metered dispenses",
        "BURN_IN_MIN_DISP_SHORT": f"{burn_in_min_dispenses:g} dispenses",
        "BURN_IN_TARGET": f"{burn_in_hours:g}-hour / {burn_in_min_dispenses:g}-dispense",
        "DUTY_HIGH": f"~{duty_cycle_high_pct:g} %",
        "DUTY_LOW": f"~{duty_cycle_low_pct:g} %",
        "DUTY_BAND": f"{duty_cycle_low_pct:g}–{duty_cycle_high_pct:g} %",
    }

    substitute_md(
        _here / "acceptance-and-burn-in.md",
        variables=variables,
        expected_counts={
            "WALL_SETPOINT": 4,
            "WALL_BAND": 2,
            "FREEZE_CUTOUT": 3,
            "MIN_OFF": 1,
            "WATER_PRESS_RANGE": 1,
            "WATER_TEMP_MAX": 1,
            "TAP_WATER_TEMP": 1,
            "CO2_CYL_SMALL": 1,
            "CO2_CYL_LARGE": 1,
            "CO2_PRIMARY_RANGE": 4,
            "CO2_CENTERLINE": 9,
            "GLASS_OZ": 9,
            "CYL_MIN": 2,
            "THERMO_RANGE": 2,
            "THERMO_ACC": 2,
            "BRIX_RANGE": 1,
            "CONC_ML": 2,
            "CONC_PCT": 2,
            "BOTTLE_L": 2,
            "PRV_HOLD": 1,
            "WALL_DISP_GATE": 1,
            "DISP_TEMP_MAX": 3,
            "DISP_TEMP_FAIL": 1,
            "FOAM_HOLD": 1,
            "RATIO": 6,
            "METERED_WATER": 1,
            "METERED_FLAVOR": 1,
            "METERED_TOTAL": 2,
            "RATIO_TOL": 1,
            "RATIO_TOL_SIGNED": 3,
            "METERED_RANGE": 1,
            "CHANNEL_TOL": 3,
            "CHANNEL_TOL_FAIL": 1,
            "RESERVOIR_FILL_PCT": 1,
            "BURN_IN_DISP": 1,
            "DISP_INTERVAL": 1,
            "BURN_IN_HOURS": 1,
            "BURN_IN_HOURS_DASH": 2,
            "BURN_IN_MIN_DISP": 2,
            "BURN_IN_MIN_DISP_SHORT": 1,
            "BURN_IN_TARGET": 1,
            "DUTY_HIGH": 1,
            "DUTY_LOW": 1,
            "DUTY_BAND": 3,
        },
    )
    print("-> acceptance-and-burn-in.md")


if __name__ == "__main__":
    main()
