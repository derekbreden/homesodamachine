"""Doc-sync driver for hardware/assembly/acceptance-and-burn-in.md.

Run: tools/cad-venv/bin/python hardware/assembly/_acceptance_and_burn_in_sync.py
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


# ─── Firmware setpoints loaded at commissioning ────────────────────────
carbonator_wall_setpoint_c = 2          # carbonator wall service temperature
carbonator_wall_band_c = 2              # hysteresis band ± around setpoint
evap_coil_freeze_cutout_c = -8          # evap-coil DS18B20 freeze-protect trip
compressor_min_off_min = 3              # compressor minimum off-time before re-energize

# ─── Bench test rig — water source ─────────────────────────────────────
bench_water_press_min_psi = 40          # bench water tap pressure, low end
bench_water_press_max_psi = 80          # bench water tap pressure, high end
bench_water_temp_max_c = 20             # bench water temperature, upper bound

# ─── Bench test rig — CO2 source ───────────────────────────────────────
co2_cyl_small_lb = 5                    # small bench cylinder
co2_cyl_large_lb = 10                   # large bench cylinder
co2_primary_min_psi = 70                # primary regulator setpoint, low end
co2_primary_max_psi = 100               # primary regulator setpoint, high end

# Centerline: matches the in-appliance WR1110 secondary regulator setpoint.
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
)                                       # fraction of one bottle consumed

# ─── Step 4 — CO2 leak-tight hold ──────────────────────────────────────
prv_hold_min = 2                        # PRV leak-tight observation window

# ─── Step 5 — first carbonated-water dispense ──────────────────────────
wall_disp_gate_c = carbonator_wall_setpoint_c + carbonator_wall_band_c
dispense_temp_max_c = 6                 # max dispensed-water temperature at the glass
foam_head_hold_sec = 10                 # minimum foam-head persistence before break

# ─── Step 6/7 — metered ratio test ─────────────────────────────────────
syrup_ratio_water = 20                  # ratio water:syrup numerator (water side)
syrup_ratio_syrup = 1                   # ratio water:syrup denominator (syrup side)
metered_water_ml = 250                  # metered carbonated-water dispense target
metered_flavor_ml = metered_water_ml / syrup_ratio_water  # = 12.5
metered_total_ml = metered_water_ml + metered_flavor_ml   # = 262.5
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
        "WALL_SETPOINT": f"{carbonator_wall_setpoint_c:.4g} °C",
        "WALL_BAND": f"± {carbonator_wall_band_c:.4g} °C",
        "FREEZE_CUTOUT": f"−{abs(evap_coil_freeze_cutout_c):.4g} °C",
        "MIN_OFF": f"{compressor_min_off_min:.4g} min",

        # Bench water rig.
        "WATER_PRESS_RANGE": f"{bench_water_press_min_psi:.4g}–{bench_water_press_max_psi:.4g} PSI",
        "WATER_TEMP_MAX": f"~{bench_water_temp_max_c:.4g} °C",
        "TAP_WATER_TEMP": f"~{bench_water_temp_max_c:.4g} °C",

        # Bench CO2 rig.
        "CO2_CYL_SMALL": f"{co2_cyl_small_lb:.4g} lb",
        "CO2_CYL_LARGE": f"{co2_cyl_large_lb:.4g} lb",
        "CO2_PRIMARY_RANGE": f"{co2_primary_min_psi:.4g}–{co2_primary_max_psi:.4g} PSI",
        "CO2_CENTERLINE": f"{co2_centerline_psi:.4g} PSI",

        # Bench measurement tooling.
        "GLASS_OZ": f"{glass_capacity_oz:.4g} oz",
        "CYL_MIN": f"{graduated_cyl_min_ml:.4g} mL",
        "THERMO_RANGE": f"{thermo_range_low_c:.4g}–{thermo_range_high_c:.4g} °C",
        "THERMO_ACC": f"±{thermo_accuracy_c:.4g} °C",
        "BRIX_RANGE": f"{refractometer_range_brix_low:.4g}–{refractometer_range_brix_high:.4g} °Brix",

        # Test-syrup consumption per unit.
        "CONC_ML": f"~{concentrate_consumed_ml_per_unit:.4g} mL",
        "CONC_PCT": f"~{concentrate_consumed_pct:.4g} %",
        "BOTTLE_L": f"{sodastream_bottle_ml / 1000:.2f} L",

        # Step 4 leak hold.
        "PRV_HOLD": f"{prv_hold_min:.4g}-minute",

        # Step 5 first carbonated dispense.
        "WALL_DISP_GATE": f"{wall_disp_gate_c:.4g} °C",
        "DISP_TEMP_MAX": f"~{dispense_temp_max_c:.4g} °C",
        "DISP_TEMP_FAIL": f"{dispense_temp_max_c:.4g} °C",
        "FOAM_HOLD": f"{foam_head_hold_sec:.4g} seconds",

        # Step 6/7 metered ratio test.
        "RATIO": f"{syrup_ratio_syrup:.4g}:{syrup_ratio_water:.4g}",
        "METERED_WATER": f"~{metered_water_ml:.4g} mL",
        "METERED_FLAVOR": f"~{metered_flavor_ml:.4g} mL",
        "METERED_TOTAL": f"~{metered_total_ml:.4g} mL",
        "RATIO_TOL": f"~{ratio_volume_tol_pct:.4g} %",
        "RATIO_TOL_SIGNED": f"±{ratio_volume_tol_pct:.4g} %",
        "METERED_RANGE": f"~{metered_total_low_ml:.4g}–{metered_total_high_ml:.4g} mL",
        "CHANNEL_TOL": f"~{channel_to_channel_tol_pct:.4g} %",
        "CHANNEL_TOL_FAIL": f"{channel_to_channel_tol_pct:.4g} %",

        # Step 11 burn-in.
        "RESERVOIR_FILL_PCT": f"~{reservoir_burnin_fill_pct:.4g} %",
        "BURN_IN_DISP": f"~{burn_in_dispense_oz:.4g} oz",
        "DISP_INTERVAL": f"{burn_in_interval_min:.4g} minutes",
        "BURN_IN_HOURS": f"{burn_in_hours:.4g} hours",
        "BURN_IN_HOURS_DASH": f"{burn_in_hours:.4g}-hour",
        "BURN_IN_MIN_DISP": f"{burn_in_min_dispenses:.4g} metered dispenses",
        "BURN_IN_MIN_DISP_SHORT": f"{burn_in_min_dispenses:.4g} dispenses",
        "BURN_IN_TARGET": f"{burn_in_hours:.4g}-hour / {burn_in_min_dispenses:.4g}-dispense",
        "DUTY_HIGH": f"~{duty_cycle_high_pct:.4g} %",
        "DUTY_LOW": f"~{duty_cycle_low_pct:.4g} %",
        "DUTY_BAND": f"{duty_cycle_low_pct:.4g}–{duty_cycle_high_pct:.4g} %",
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
