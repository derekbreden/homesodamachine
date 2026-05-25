"""Compressor-shroud dimensions — source-of-truth constants for the
sheet-metal shroud over the compressor terminal block.

No generator script yet (the shroud's dimensions are still TBD,
pending donor-compressor measurement — see ../../harvested/ice-maker/
"Open items"). This module exists as the dimension source that the
README's [value](NAME) markers substitute against, so prose and
numbers stay in sync once measurements arrive and constants here are
updated.

Run as a script to substitute the README:

    tools/cad-venv/bin/python _compressor_shroud_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md, substitute_py_comments


# ─── Compressor envelope (placeholders — revise after measurement) ────
# Source: rough estimate for a 100 W-class hermetic; donor is
# HD48Y11 (Antarctic Star HZB-12/Q) or equivalent in Frigidaire
# EFIC117-SS. See ../../harvested/ice-maker/README.md.

compressor_body_od_mm = 95              # compressor body OD
compressor_body_height_mm = 110         # compressor body height
compressor_class_w = 100                # cooling-capacity class
terminal_block_width_mm = 50            # terminal + PTC envelope, X
terminal_block_height_mm = 40           # terminal + PTC envelope, Z (vertical)
terminal_block_standoff_mm = 30         # PTC module radial standoff above pins
terminal_block_clearance_mm = 10        # min internal clearance to terminal block
ptc_surface_temp_c = 150                # PTC module operating temp (~140–150 °C)
ptc_surface_temp_low_c = 140            # low end of PTC operating range

# ─── Shroud working envelope (placeholders — revise after measurement) ──
outer_x_mm = 130                        # depth into appliance
outer_y_mm = 130                        # width across appliance
outer_z_mm = 100                        # vertical height above floor
internal_headroom_mm = 20               # min headroom over compressor
flange_height_low_mm = 90               # side wall flange height, low end of range
flange_height_high_mm = 100             # side wall flange height, high end of range

# ─── Material spec (SendCutSend 0.059" G90 hot-dipped galvanized) ────
# Source: SendCutSend material catalog,
# sendcutsend.com/materials/g90-steel/ (.059" tab).

wall_thickness_in = 0.059               # G90 sheet thickness, 16-gauge nominal
wall_thickness_mm = 1.50                # = 0.059" rounded to two decimals
alt_thickness_low_in = 0.030            # alternate G90 thicknesses (thinner)
alt_thickness_mid_in = 0.036
alt_thickness_high_in = 0.048
alt_thickness_thicker_in = 0.074        # one step thicker than chosen
design_life_yr = 10                     # G90 coating life in humid-kitchen ambient
cost_low_usd = 5                        # per-part cost at qty 5–10
cost_high_usd = 10
order_qty_low = 5
order_qty_high = 10

# ─── Penetrations ─────────────────────────────────────────────────────
# Sources: AWG and JIS / metric standards; Heyco SB-500-6 datasheet
# (cable OD 5.6–6.4 mm); 18 AWG SJOOW outer diameter from cable spec.
ac_cable_awg = 18                       # SJOOW bundle gauge
ac_cable_od_mm = 6.4                    # 18 AWG SJOOW measured OD
bushing_cable_od_low_mm = 5.6           # Heyco SB-500-6 cable-OD range, low
bushing_cable_od_high_mm = 6.4          # Heyco SB-500-6 cable-OD range, high
panel_hole_in = 0.5                     # 1/2" panel hole for Heyco SB-500-6
panel_hole_label = '1/2"'               # display label (inch fraction reads better than 0.5")
alt_panel_hole_in = 0.625               # 5/8" alternative considered, rejected
alt_panel_hole_label = '5/8"'           # display label (inch fraction reads better than 0.625")
panel_hole_area_saving_pct = 36         # 1/2" removes 36% less metal than 5/8"
mounting_tab_thread = "M3"              # shroud-side mounting tab thread
mounting_foot_thread = "M5"             # compressor's mounting feet thread
chassis_ground_hole_mm = 6              # Ø chassis bonding stud hole

# ─── SendCutSend laser-cut + bend specs (0.059" G90) ──────────────────
# Source: SendCutSend material catalog,
# sendcutsend.com/materials/g90-steel/ (.059" tab).

cut_tolerance_in = 0.005                # ±, laser cut tolerance
min_hole_d_in = 0.022                   # minimum hole diameter
min_hole_d_mm = 0.56                    # = 0.022" rounded
min_hole_to_edge_in = 0.020             # min spacing of a hole edge to part edge
min_hole_to_edge_mm = 0.51              # = 0.020" rounded
min_part_w_in = 0.25                    # min part dimension (X)
min_part_h_in = 0.375                   # min part dimension (Y)
min_bend_w_in = 0.375                   # min part dimension for any bend (X)
min_bend_h_in = 1.5                     # min part dimension for any bend (Y)
max_bend_length_in = 44                 # max linear bend length
min_flange_in = 0.311                   # min flange length after 90° bend
min_flange_mm = 7.9                     # = 0.311" rounded
bend_radius_in = 0.063                  # effective bend radius @ 90°
bend_radius_mm = 1.6                    # = 0.063" rounded
bend_deduction_in = 0.112               # bend deduction @ 90°
k_factor = 0.36                         # neutral-axis K factor
bend_angle_tolerance_deg = 1            # ±, for bend length ≤ 24"
bend_length_for_tol_in = 24             # bend length below which the ±1° applies
max_box_flange_in = 3.0                 # max 4-sided box flange height with hardware
max_box_flange_mm = 76                  # = 3.00" rounded
hole_to_bend_in = 0.15                  # 1.5×T + R rule of thumb
hole_to_bend_mm = 3.8                   # = 0.15" rounded
hardware_min_w_in = 1.0                 # PEM hardware insertion min size (X)
hardware_min_h_in = 1.5                 # PEM hardware insertion min size (Y)
tap_thread_size = "M3 × 0.5"            # tappable thread on this thickness
bend_angle_deg = 90                     # all bends are 90°

# ─── Donor-compressor / external-references (informational) ───────────
ac_voltage_v = 12                       # condenser fan motor DC bus voltage


def main():
    variables = {
        # Compressor envelope.
        "COMP_OD": f"{compressor_body_od_mm:g} mm",
        "COMP_H": f"{compressor_body_height_mm:g} mm",
        "COMP_CLASS_W": f"{compressor_class_w:g} W",
        "TB_W": f"{terminal_block_width_mm:g} mm",
        "TB_H": f"{terminal_block_height_mm:g} mm",
        "TB_STANDOFF": f"{terminal_block_standoff_mm:g} mm",
        "TB_CLEARANCE": f"{terminal_block_clearance_mm:g} mm",
        "PTC_TEMP_LOW": f"{ptc_surface_temp_low_c:g}",
        "PTC_TEMP": f"{ptc_surface_temp_c:g} °C",
        # Shroud working envelope.
        "OUTER_X": f"{outer_x_mm:g} mm",
        "OUTER_Y": f"{outer_y_mm:g} mm",
        "OUTER_Z": f"{outer_z_mm:g} mm",
        "HEADROOM": f"{internal_headroom_mm:g} mm",
        "FLANGE_LOW": f"{flange_height_low_mm:g}",
        "FLANGE_HIGH": f"{flange_height_high_mm:g} mm",
        # Material spec.
        "WALL_IN": f"{wall_thickness_in:g}\"",
        "WALL_MM": f"{wall_thickness_mm:g} mm",
        "ALT_THK_LOW": f"{alt_thickness_low_in:g}″",
        "ALT_THK_MID": f"{alt_thickness_mid_in:g}″",
        "ALT_THK_HIGH": f"{alt_thickness_high_in:g}″",
        "ALT_THK_THICKER": f"{alt_thickness_thicker_in:g}\"",
        "DESIGN_LIFE": f"{design_life_yr:g}-year",
        "COST_LOW": f"${cost_low_usd:g}",
        "COST_HIGH": f"${cost_high_usd:g}",
        "QTY_LOW": f"{order_qty_low:g}",
        "QTY_HIGH": f"{order_qty_high:g}",
        # Penetrations.
        "AC_AWG": f"{ac_cable_awg:g} AWG",
        "AC_OD": f"{ac_cable_od_mm:g} mm",
        "BUSHING_LOW": f"{bushing_cable_od_low_mm:g}",
        "BUSHING_HIGH": f"{bushing_cable_od_high_mm:g} mm",
        "PANEL_HOLE": panel_hole_label,
        "ALT_PANEL_HOLE": alt_panel_hole_label,
        "AREA_SAVING": f"{panel_hole_area_saving_pct:g}%",
        "TAB_THREAD": f"{mounting_tab_thread}",
        "FOOT_THREAD": f"{mounting_foot_thread}",
        "GND_HOLE": f"{chassis_ground_hole_mm:g} mm",
        # SendCutSend specs.
        "CUT_TOL": f"±{cut_tolerance_in:g}\"",
        "MIN_HOLE_IN": f"{min_hole_d_in:g}\"",
        "MIN_HOLE_MM": f"{min_hole_d_mm:g} mm",
        "MIN_HE_IN": f"{min_hole_to_edge_in:g}\"",
        "MIN_HE_MM": f"{min_hole_to_edge_mm:g} mm",
        "MIN_PART": f"{min_part_w_in:g}\" × {min_part_h_in:g}\"",
        "MIN_BEND_PART": f"{min_bend_w_in:g}\" × {min_bend_h_in:g}\"",
        "MAX_BEND_LEN": f"{max_bend_length_in:g}\"",
        "MIN_FLANGE_IN": f"{min_flange_in:g}\"",
        "MIN_FLANGE_MM": f"{min_flange_mm:g} mm",
        "BEND_R_IN": f"{bend_radius_in:g}\"",
        "BEND_R_MM": f"{bend_radius_mm:g} mm",
        "BEND_DED": f"{bend_deduction_in:g}\"",
        "K_FACTOR": f"{k_factor:g}",
        "BEND_TOL": f"±{bend_angle_tolerance_deg:g}°",
        "BEND_TOL_LEN": f"{bend_length_for_tol_in:g}\"",
        "MAX_BOX_IN": f"{max_box_flange_in:.2f}\"",
        "MAX_BOX_MM": f"{max_box_flange_mm:g} mm",
        "HTB_IN": f"{hole_to_bend_in:g}\"",
        "HTB_MM": f"{hole_to_bend_mm:g} mm",
        "HW_MIN": f"{hardware_min_w_in:g}\" × {hardware_min_h_in:g}\"",
        "TAP_THREAD": tap_thread_size,
        "BEND_ANGLE": f"{bend_angle_deg:g}°",
        # External references.
        "FAN_V": f"{ac_voltage_v:g} V",
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
            "PTC_TEMP": 2,
            "OUTER_X": 1,
            "OUTER_Y": 1,
            "OUTER_Z": 1,
            "HEADROOM": 1,
            "FLANGE_LOW": 1,
            "FLANGE_HIGH": 1,
            "WALL_IN": 4,
            "WALL_MM": 1,
            "ALT_THK_LOW": 1,
            "ALT_THK_MID": 1,
            "ALT_THK_HIGH": 1,
            "ALT_THK_THICKER": 1,
            "DESIGN_LIFE": 1,
            "COST_LOW": 1,
            "COST_HIGH": 1,
            "QTY_LOW": 1,
            "QTY_HIGH": 1,
            "AC_AWG": 3,
            "AC_OD": 1,
            "BUSHING_LOW": 1,
            "BUSHING_HIGH": 1,
            "PANEL_HOLE": 2,
            "ALT_PANEL_HOLE": 1,
            "AREA_SAVING": 1,
            "TAB_THREAD": 3,
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
            "BEND_DED": 2,
            "K_FACTOR": 1,
            "BEND_TOL": 1,
            "BEND_TOL_LEN": 1,
            "MAX_BOX_IN": 4,
            "MAX_BOX_MM": 2,
            "HTB_IN": 1,
            "HTB_MM": 1,
            "HW_MIN": 1,
            "TAP_THREAD": 1,
            "BEND_ANGLE": 4,
            "FAN_V": 3,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
