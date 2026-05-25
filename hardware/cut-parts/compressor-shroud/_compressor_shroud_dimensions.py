"""Doc-sync driver for hardware/cut-parts/compressor-shroud/README.md.

Run: tools/cad-venv/bin/python hardware/cut-parts/compressor-shroud/_compressor_shroud_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md


# Compressor envelope (placeholders — revise after measurement).
compressor_body_od_mm = 95
compressor_body_height_mm = 110
compressor_class_w = 100
terminal_block_width_mm = 50
terminal_block_height_mm = 40
terminal_block_standoff_mm = 30
terminal_block_clearance_mm = 10
ptc_surface_temp_c = 150
ptc_surface_temp_low_c = 140

# Shroud working envelope (placeholders — revise after measurement).
outer_x_mm = 130
outer_y_mm = 130
outer_z_mm = 100
internal_headroom_mm = 20
flange_height_low_mm = 90
flange_height_high_mm = 100

# Material — SendCutSend 0.059" G90 hot-dipped galvanized.
wall_thickness_in = 0.059
wall_thickness_mm = 1.50
design_life_yr = 10
cost_low_usd = 5
cost_high_usd = 10
order_qty_low = 5
order_qty_high = 10

# Penetrations.
ac_cable_awg = 18
ac_cable_od_mm = 6.4
bushing_cable_od_low_mm = 5.6
bushing_cable_od_high_mm = 6.4
panel_hole_label = '1/2"'
mounting_tab_thread = "M3"
mounting_foot_thread = "M5"
chassis_ground_hole_mm = 6

# SendCutSend laser-cut + bend specs for 0.059" G90.
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
bend_radius_in = 0.063
bend_radius_mm = 1.6
bend_deduction_in = 0.112
k_factor = 0.36
bend_angle_tolerance_deg = 1
bend_length_for_tol_in = 24
max_box_flange_in = 3.0
max_box_flange_mm = 76
hole_to_bend_in = 0.15
hole_to_bend_mm = 3.8
hardware_min_w_in = 1.0
hardware_min_h_in = 1.5
tap_thread_size = "M3 × 0.5"
bend_angle_deg = 90

# External references.
ac_voltage_v = 12


def main():
    variables = {
        "COMP_OD": f"{compressor_body_od_mm:.4g} mm",
        "COMP_H": f"{compressor_body_height_mm:.4g} mm",
        "COMP_CLASS_W": f"{compressor_class_w:.4g} W",
        "TB_W": f"{terminal_block_width_mm:.4g} mm",
        "TB_H": f"{terminal_block_height_mm:.4g} mm",
        "TB_STANDOFF": f"{terminal_block_standoff_mm:.4g} mm",
        "TB_CLEARANCE": f"{terminal_block_clearance_mm:.4g} mm",
        "PTC_TEMP_LOW": f"{ptc_surface_temp_low_c:.4g}",
        "PTC_TEMP": f"{ptc_surface_temp_c:.4g} °C",
        "OUTER_X": f"{outer_x_mm:.4g} mm",
        "OUTER_Y": f"{outer_y_mm:.4g} mm",
        "OUTER_Z": f"{outer_z_mm:.4g} mm",
        "HEADROOM": f"{internal_headroom_mm:.4g} mm",
        "FLANGE_LOW": f"{flange_height_low_mm:.4g}",
        "FLANGE_HIGH": f"{flange_height_high_mm:.4g} mm",
        "WALL_IN": f"{wall_thickness_in:.4g}\"",
        "WALL_MM": f"{wall_thickness_mm:.4g} mm",
        "DESIGN_LIFE": f"{design_life_yr:.4g}-year",
        "COST_LOW": f"${cost_low_usd:.4g}",
        "COST_HIGH": f"${cost_high_usd:.4g}",
        "QTY_LOW": f"{order_qty_low:.4g}",
        "QTY_HIGH": f"{order_qty_high:.4g}",
        "AC_AWG": f"{ac_cable_awg:.4g} AWG",
        "AC_OD": f"{ac_cable_od_mm:.4g} mm",
        "BUSHING_LOW": f"{bushing_cable_od_low_mm:.4g}",
        "BUSHING_HIGH": f"{bushing_cable_od_high_mm:.4g} mm",
        "PANEL_HOLE": panel_hole_label,
        "TAB_THREAD": f"{mounting_tab_thread}",
        "FOOT_THREAD": f"{mounting_foot_thread}",
        "GND_HOLE": f"{chassis_ground_hole_mm:.4g} mm",
        "CUT_TOL": f"±{cut_tolerance_in:.4g}\"",
        "MIN_HOLE_IN": f"{min_hole_d_in:.4g}\"",
        "MIN_HOLE_MM": f"{min_hole_d_mm:.4g} mm",
        "MIN_HE_IN": f"{min_hole_to_edge_in:.4g}\"",
        "MIN_HE_MM": f"{min_hole_to_edge_mm:.4g} mm",
        "MIN_PART": f"{min_part_w_in:.4g}\" × {min_part_h_in:.4g}\"",
        "MIN_BEND_PART": f"{min_bend_w_in:.4g}\" × {min_bend_h_in:.4g}\"",
        "MAX_BEND_LEN": f"{max_bend_length_in:.4g}\"",
        "MIN_FLANGE_IN": f"{min_flange_in:.4g}\"",
        "MIN_FLANGE_MM": f"{min_flange_mm:.4g} mm",
        "BEND_R_IN": f"{bend_radius_in:.4g}\"",
        "BEND_R_MM": f"{bend_radius_mm:.4g} mm",
        "BEND_DED": f"{bend_deduction_in:.4g}\"",
        "K_FACTOR": f"{k_factor:.4g}",
        "BEND_TOL": f"±{bend_angle_tolerance_deg:.4g}°",
        "BEND_TOL_LEN": f"{bend_length_for_tol_in:.4g}\"",
        "MAX_BOX_IN": f"{max_box_flange_in:.2f}\"",
        "MAX_BOX_MM": f"{max_box_flange_mm:.4g} mm",
        "HTB_IN": f"{hole_to_bend_in:.4g}\"",
        "HTB_MM": f"{hole_to_bend_mm:.4g} mm",
        "HW_MIN": f"{hardware_min_w_in:.4g}\" × {hardware_min_h_in:.4g}\"",
        "TAP_THREAD": tap_thread_size,
        "BEND_ANGLE": f"{bend_angle_deg:.4g}°",
        "FAN_V": f"{ac_voltage_v:.4g} V",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "COMP_OD": 1,
            "COMP_H": 1,
            "COMP_CLASS_W": 1,
            "TB_W": 1,
            "TB_H": 1,
            "TB_STANDOFF": 1,
            "TB_CLEARANCE": 1,
            "PTC_TEMP_LOW": 1,
            "PTC_TEMP": 1,
            "OUTER_X": 1,
            "OUTER_Y": 1,
            "OUTER_Z": 1,
            "HEADROOM": 1,
            "FLANGE_LOW": 1,
            "FLANGE_HIGH": 1,
            "WALL_IN": 3,
            "WALL_MM": 1,
            "DESIGN_LIFE": 1,
            "COST_LOW": 1,
            "COST_HIGH": 1,
            "QTY_LOW": 1,
            "QTY_HIGH": 1,
            "AC_AWG": 3,
            "AC_OD": 1,
            "BUSHING_LOW": 1,
            "BUSHING_HIGH": 1,
            "PANEL_HOLE": 1,
            "TAB_THREAD": 2,
            "FOOT_THREAD": 4,
            "GND_HOLE": 1,
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
            "BEND_R_IN": 1,
            "BEND_R_MM": 1,
            "BEND_DED": 1,
            "K_FACTOR": 1,
            "BEND_TOL": 1,
            "BEND_TOL_LEN": 1,
            "MAX_BOX_IN": 1,
            "MAX_BOX_MM": 1,
            "HTB_IN": 1,
            "HTB_MM": 1,
            "HW_MIN": 1,
            "TAP_THREAD": 1,
            "BEND_ANGLE": 3,
            "FAN_V": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
