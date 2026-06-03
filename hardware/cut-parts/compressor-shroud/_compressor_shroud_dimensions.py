"""Canonical dimensions for the compressor shroud.

Single source of truth for the part's scalars. `compressor_shroud.py`
imports the geometry from here to build the STEP + flat DXF; the assembly
doc-sync drivers `_wiring_sync.py` and `_enclosure_mechanical_sync.py`
import the cross-referenced electrical/mechanical values; and this file's
own `main()` drives `README.md`.

Run: tools/cad-venv/bin/python hardware/cut-parts/compressor-shroud/_compressor_shroud_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md  # noqa: E402

_MM_PER_IN = 25.4

# ── Interior envelope (user spec) ──────────────────────────────────
interior_width_mm = 130.0    # W
interior_depth_mm = 175.0    # D
interior_height_mm = 150.0   # H

# ── Material — SendCutSend G90 hot-dipped galvanized, 0.059" ────────
wall_thickness_in = 0.059
wall_thickness_mm = wall_thickness_in * _MM_PER_IN
inside_bend_radius_in = 0.063
inside_bend_radius_mm = inside_bend_radius_in * _MM_PER_IN
k_factor = 0.36
bend_angle_deg = 90
design_life_yr = 10

# Outer envelope: each wall + the top add one wall thickness.
outer_width_mm = interior_width_mm + 2 * wall_thickness_mm
outer_depth_mm = interior_depth_mm + 2 * wall_thickness_mm
outer_height_mm = interior_height_mm + wall_thickness_mm

# ── Penetrations ───────────────────────────────────────────────────
ac_hole_diameter_in = 0.5
ac_hole_diameter_mm = ac_hole_diameter_in * _MM_PER_IN
panel_hole_label = '1/2"'          # AC pass-through; imported by enclosure sync
copper_tube_od_label = '1/4"'
copper_tube_od_mm = 6.35
copper_hole_diameter_mm = 8.0
mounting_hole_diameter_mm = 4.5    # M4 clearance — fastens to the enclosure floor

# ── Cross-referenced electrical / mechanical values ────────────────
# Imported by /hardware/assembly/_wiring_sync.py and
# _enclosure_mechanical_sync.py — keep these names stable.
ac_cable_awg = 18
ac_cable_od_mm = 6.4
bushing_cable_od_low_mm = 5.6
bushing_cable_od_high_mm = 6.4
chassis_ground_hole_mm = 6           # earth-bond point if added (see README "Grounding")
compressor_class_w = 100
terminal_block_clearance_mm = 10

# ── What the shroud houses ─────────────────────────────────────────
compressor_body_od_mm = 95
compressor_body_height_mm = 110
ptc_surface_temp_c = 150
ptc_surface_temp_low_c = 140
ac_voltage_v = 12                    # condenser fan (DC)

# ── SendCutSend laser + bend specs for 0.059" G90 ──────────────────
cut_tolerance_in = 0.005
min_hole_d_in = 0.022
min_hole_d_mm = 0.56
min_hole_to_edge_in = 0.020
min_hole_to_edge_mm = 0.51
min_part_w_in = 0.25
min_part_h_in = 0.375
min_bend_w_in = 0.375
min_bend_h_in = 1.5
max_bend_length_in = 44
min_flange_in = 0.311
min_flange_mm = 7.9
bend_deduction_in = 0.112            # SendCutSend's published 90° value
bend_angle_tolerance_deg = 1
bend_length_for_tol_in = 24
max_box_flange_in = 3.0
max_box_flange_mm = 76
hole_to_bend_in = 0.15
hole_to_bend_mm = 3.8
hardware_min_w_in = 1.0
hardware_min_h_in = 1.5
tap_thread_size = "M3 × 0.5"


def main():
    variables = {
        # What it covers.
        "COMP_OD": f"{compressor_body_od_mm:.4g} mm",
        "COMP_H": f"{compressor_body_height_mm:.4g} mm",
        "COMP_CLASS_W": f"{compressor_class_w:.4g} W",
        "PTC_TEMP_LOW": f"{ptc_surface_temp_low_c:.4g}",
        "PTC_TEMP": f"{ptc_surface_temp_c:.4g} °C",
        "AC_AWG": f"{ac_cable_awg:.4g} AWG",
        "FAN_V": f"{ac_voltage_v:.4g} V",
        # Dimensions.
        "INT_W": f"{interior_width_mm:.4g} mm",
        "INT_D": f"{interior_depth_mm:.4g} mm",
        "INT_H": f"{interior_height_mm:.4g} mm",
        "OUT_W": f"{outer_width_mm:.4g} mm",
        "OUT_D": f"{outer_depth_mm:.4g} mm",
        "OUT_H": f"{outer_height_mm:.4g} mm",
        "TB_CLEARANCE": f"{terminal_block_clearance_mm:.4g} mm",
        # Material.
        "WALL_IN": f'{wall_thickness_in:.4g}"',
        "WALL_MM": f"{wall_thickness_mm:.4g} mm",
        "DESIGN_LIFE": f"{design_life_yr:.4g}-year",
        "BEND_R_IN": f'{inside_bend_radius_in:.4g}"',
        "BEND_R_MM": f"{inside_bend_radius_mm:.4g} mm",
        "K_FACTOR": f"{k_factor:.4g}",
        # Penetrations.
        "PANEL_HOLE": panel_hole_label,
        "AC_HOLE_MM": f"{ac_hole_diameter_mm:.4g} mm",
        "BUSHING_LOW": f"{bushing_cable_od_low_mm:.4g}",
        "BUSHING_HIGH": f"{bushing_cable_od_high_mm:.4g} mm",
        "AC_OD": f"{ac_cable_od_mm:.4g} mm",
        "CU_HOLE": f"{copper_hole_diameter_mm:.4g} mm",
        "CU_OD": copper_tube_od_label,
        # Grounding + mounting.
        "GND_HOLE": f"{chassis_ground_hole_mm:.4g} mm",
        "MOUNT_HOLE": f"{mounting_hole_diameter_mm:.4g} mm",
        # SendCutSend specs.
        "CUT_TOL": f'±{cut_tolerance_in:.4g}"',
        "MIN_HOLE_IN": f'{min_hole_d_in:.4g}"',
        "MIN_HOLE_MM": f"{min_hole_d_mm:.4g} mm",
        "MIN_HE_IN": f'{min_hole_to_edge_in:.4g}"',
        "MIN_HE_MM": f"{min_hole_to_edge_mm:.4g} mm",
        "MIN_PART": f'{min_part_w_in:.4g}" × {min_part_h_in:.4g}"',
        "MIN_BEND_PART": f'{min_bend_w_in:.4g}" × {min_bend_h_in:.4g}"',
        "MAX_BEND_LEN": f'{max_bend_length_in:.4g}"',
        "MIN_FLANGE_IN": f'{min_flange_in:.4g}"',
        "MIN_FLANGE_MM": f"{min_flange_mm:.4g} mm",
        "BEND_DED": f'{bend_deduction_in:.4g}"',
        "BEND_TOL": f"±{bend_angle_tolerance_deg:.4g}°",
        "BEND_TOL_LEN": f'{bend_length_for_tol_in:.4g}"',
        "MAX_BOX_IN": f'{max_box_flange_in:.2f}"',
        "MAX_BOX_MM": f"{max_box_flange_mm:.4g} mm",
        "HTB_IN": f'{hole_to_bend_in:.4g}"',
        "HTB_MM": f"{hole_to_bend_mm:.4g} mm",
        "HW_MIN": f'{hardware_min_w_in:.4g}" × {hardware_min_h_in:.4g}"',
        "TAP_THREAD": tap_thread_size,
        "BEND_ANGLE": f"{bend_angle_deg:.4g}°",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "COMP_OD": 1,
            "COMP_H": 1,
            "COMP_CLASS_W": 1,
            "PTC_TEMP_LOW": 1,
            "PTC_TEMP": 1,
            "AC_AWG": 3,
            "FAN_V": 1,
            "INT_W": 1,
            "INT_D": 1,
            "INT_H": 1,
            "OUT_W": 1,
            "OUT_D": 1,
            "OUT_H": 1,
            "TB_CLEARANCE": 1,
            "WALL_IN": 2,
            "WALL_MM": 1,
            "DESIGN_LIFE": 1,
            "BEND_R_IN": 2,
            "BEND_R_MM": 2,
            "K_FACTOR": 2,
            "PANEL_HOLE": 1,
            "AC_HOLE_MM": 1,
            "BUSHING_LOW": 1,
            "BUSHING_HIGH": 1,
            "AC_OD": 1,
            "CU_HOLE": 2,
            "CU_OD": 2,
            "GND_HOLE": 2,
            "MOUNT_HOLE": 2,
            "CUT_TOL": 1,
            "MIN_HOLE_IN": 1,
            "MIN_HOLE_MM": 1,
            "MIN_HE_IN": 1,
            "MIN_HE_MM": 1,
            "MIN_PART": 1,
            "MIN_BEND_PART": 1,
            "MAX_BEND_LEN": 1,
            "MIN_FLANGE_IN": 1,
            "MIN_FLANGE_MM": 1,
            "BEND_DED": 1,
            "BEND_TOL": 1,
            "BEND_TOL_LEN": 1,
            "MAX_BOX_IN": 1,
            "MAX_BOX_MM": 1,
            "HTB_IN": 1,
            "HTB_MM": 1,
            "HW_MIN": 1,
            "TAP_THREAD": 1,
            "BEND_ANGLE": 3,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
