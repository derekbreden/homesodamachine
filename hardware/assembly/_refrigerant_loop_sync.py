"""Doc-sync driver for hardware/assembly/refrigerant-loop.md.

Run: tools/cad-venv/bin/python hardware/assembly/_refrigerant_loop_sync.py
"""

import math
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


# Coil tie-in stubs — owned by the coil-mandrel generator alongside the wrap arc
# they extend. What this procedure sees is the PROTRUDING half of each allowance;
# the rest of it is the tail's own run inside the shell, already foamed in.
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

# ─── Brazing heat vs. the printed copper-plug stack ───────────────────
# The copper leaves the core through PRINTED PETG plugs and the joints are
# brazed a few tube-diameters off their faces, so the plug is downstream of a
# ~700 °C torch on a conductor. What that costs is estimated, not measured:
# a straight-fin decay length L = sqrt(k·A / (h·P)) on 1/4" OD × 0.031" wall
# copper, then the plug face read at exp(−x/L) of the joint's rise.

petg_glass_transition_c = 80            # PETG Tg — the plug's own ceiling
braze_joint_temp_c = 700                # BCuP-5 working temperature
ambient_c = 20                          # shop ambient the rise is over
copper_k_w_mk = 380                     # 1/4" ACR copper conductivity
fin_h_w_m2k = 35                        # natural convection + radiation, combined
joint_standoff_mm = 67.7                # refrig-3's own reach — `_lines` draws no longer one

_tube_od_mm = 6.35                      # 1/4" OD
_tube_wall_mm = 0.031 * 25.4            # 0.031" wall
_tube_id_mm = _tube_od_mm - 2 * _tube_wall_mm
# Section the heat runs down, and the surface it leaves by, in SI.
_area_m2 = math.pi / 4 * (_tube_od_mm ** 2 - _tube_id_mm ** 2) / 1e6
_perimeter_m = math.pi * _tube_od_mm / 1e3
fin_decay_mm = math.sqrt(copper_k_w_mk * _area_m2 / (fin_h_w_m2k * _perimeter_m)) * 1e3
plug_face_rise_c = ((braze_joint_temp_c - ambient_c)
                    * math.exp(-joint_standoff_mm / fin_decay_mm))


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
        # Coil tie-in stubs (coil_mandrel.py) — the PROTRUDING half of each allowance.
        "PROT_INLET": f"{_coil_mandrel_gen.stub_protrusion['inlet']:.4g} mm",
        "PROT_OUTLET": f"{_coil_mandrel_gen.stub_protrusion['outlet']:.4g} mm",
        # Brazing heat against the printed copper-plug stack.
        "PETG_TG": f"~{petg_glass_transition_c:.4g} °C",
        "BRAZE_TEMP": f"~{braze_joint_temp_c:.4g} °C",
        "COPPER_K": f"{copper_k_w_mk:.4g} W/m·K",
        "FIN_H": f"{fin_h_w_m2k:.4g} W/m²K",
        "JOINT_STANDOFF": f"~{joint_standoff_mm:.4g} mm",
        "FIN_DECAY": f"{fin_decay_mm:.1f} mm",
        "PLUG_RISE": f"~{plug_face_rise_c:.0f} °C",
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
            "PROT_INLET": 2,
            "PROT_OUTLET": 2,
            "PETG_TG": 1,
            "BRAZE_TEMP": 1,
            "COPPER_K": 1,
            "FIN_H": 1,
            "JOINT_STANDOFF": 2,
            "FIN_DECAY": 1,
            "PLUG_RISE": 1,
        },
    )
    print("-> refrigerant-loop.md")


if __name__ == "__main__":
    main()
