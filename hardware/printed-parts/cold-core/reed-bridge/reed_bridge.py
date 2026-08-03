"""Carbonator reed bridge — printed PETG interposer holding the two
external level reeds against the vessel wall on the register azimuth,
standing the evaporator coil off the glass where a wrap crosses it.

The donut is an axially-magnetised ferrite ring: radially outside it, on
its mid-plane, the field is purely axial, so both reeds stand with their
glass vertical. reed_glass_length of vertical glass spans one wrap or two
at the wind's inter_wrap_clear.

The plateau stands pocket_depth off the steel; each reed lies in a pocket
cut clear through to the wall, so its glass rests on bare 316L. Ramps on
all four sides are what each wrap rides over as the coil is dragged down
the vessel. Copper hoop tension clamps the bridge to the wall; the foam
pour sets it.

The setting gauge hangs on the tube's bottom rim and its top face is
bridge_z_bottom.

Frame: +Z is the vessel axis, Z=0 at the tube's bottom rim — the face
that seats on the tank support ring. +X is the register azimuth, the line
the wall-preloaded donut rides. The part is symmetric about the XZ plane
apart from the lead groove.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hardware = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hardware / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_here.parents[1]))
sys.path.insert(0, str(_here.parents[1] / "copper-plugs"))
sys.path.insert(0, str(_here.parents[1] / "coil-mandrel"))
sys.path.insert(0, str(_hardware / "cut-parts" / "carbonation" / "endcaps-circular"))
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments
from _cold_core_interface import (
    tank_outer_radius,
    tank_height,
    tank_support_ring_height,
    wall_and_floor_thickness,
)
from _cold_core_interface import evap_tail_low_z, evap_tail_high_z
from coil_mandrel import pitch, tube_radius, wrap_length
from endcap_circular_dxf import (
    tube_id,
    donut_od,
    register_radius,
    disc_thickness,
)


# ═══════════════════════════════════════════════════════
# THE WALL THE BRIDGE SITS ON
# ═══════════════════════════════════════════════════════

# The tube's bottom rim rests on the tank support ring, so the vessel's
# own Z=0 is that far up the foam shell.
tube_bottom_z_in_shell = wall_and_floor_thickness + tank_support_ring_height

# [15 mm](BAND_BOTTOM) / [134.4 mm](BAND_TOP) — lowest and highest coil
# centreline on the tube. Read from where the TAILS leave the tank, not from where
# their copper crosses the shell wall: the two part company (each tail climbs the
# port lane to its station), and reading the crossing here would let the front port
# field compress the coil.
band_bottom_z = evap_tail_low_z - tube_bottom_z_in_shell
band_top_z = evap_tail_high_z - tube_bottom_z_in_shell

# [6.35 mm](COPPER_OD) — 1/4" ACR wrap.
copper_od = 2 * tube_radius
# [5.976 mm](INTER_WRAP_CLEAR) — bare wall between adjacent wraps at one
# azimuth, at [12.33 mm](WRAP_PITCH) pitch. A [14 mm](REED_GLASS_L) span
# standing vertical crosses one wrap or two.
inter_wrap_clear = pitch - copper_od


# ═══════════════════════════════════════════════════════
# THE WATER COLUMN THE REEDS READ
# ═══════════════════════════════════════════════════════

# Each end plate is an ID-fit plug seated one plate-thickness' worth of
# recess below its tube end, so the wetted column runs between the two
# inside faces.
plate_recess = disc_thickness * 25.4
plate_thickness = disc_thickness * 25.4
interior_floor_z = plate_recess + plate_thickness  # [12.7 mm](INTERIOR_FLOOR)
interior_ceiling_z = tank_height - plate_recess - plate_thickness  # [139.7 mm](INTERIOR_CEILING)
# [127 mm](INTERIOR_H) of wetted height inside a [123.7 mm](TUBE_ID_MM) bore.
interior_height = interior_ceiling_z - interior_floor_z

tube_id_mm = tube_id * 25.4
interior_area = math.pi / 4 * tube_id_mm**2
# [12.02 mL](ML_PER_MM) of water per mm of level; [1526 mL](INTERIOR_ML) if it were full.
volume_per_mm = interior_area / 1000
interior_volume_ml = volume_per_mm * interior_height

serving_volume_ml = 355.0  # 12 US fl oz, the app's default serving
syrup_dilution = 20.0      # 1 part SodaStream-compatible syrup : 20 parts water
# [338.1 mL](WATER_PER_SERVING) of carbonated water per serving —
# [28.13 mm](SERVING_RISE) of level.
carbonated_water_per_serving = (
    serving_volume_ml * syrup_dilution / (syrup_dilution + 1)
)
serving_level_rise = carbonated_water_per_serving / volume_per_mm

# Pump-off level, as a fraction of the wetted height. The complement is
# the CO2 headspace the sparge column and the level surge live in.
high_fill_fraction = 0.65
# [95.25 mm](HIGH_LEVEL) — CHI, pump off. [67.12 mm](LOW_LEVEL) — CLO,
# pump on, one serving below.
high_level_z = interior_floor_z + high_fill_fraction * interior_height
low_level_z = high_level_z - serving_level_rise

headspace_height = interior_ceiling_z - high_level_z
headspace_ml = headspace_height * volume_per_mm
reserve_height = low_level_z - interior_floor_z
reserve_ml = reserve_height * volume_per_mm
stored_ml = (high_level_z - interior_floor_z) * volume_per_mm

# Height of the donut's magnetic mid-plane above the water surface it rides.
magnet_lead_above_surface = 0.0
reed_low_z = low_level_z + magnet_lead_above_surface
reed_high_z = high_level_z + magnet_lead_above_surface


# ═══════════════════════════════════════════════════════
# THE DONUT'S REACH
# ═══════════════════════════════════════════════════════

float_height = 12.0     # donor YXQ capsule, magnet ring taken as centred
rod_tack_fillet = 1.5   # the tack bead the donut lands on at the rod base

# [20.2 mm](MAGNET_LOWEST) to [133.7 mm](MAGNET_HIGHEST) — where the
# donut's mid-plane can be, between the tack bead and the top plate.
magnet_lowest_z = interior_floor_z + rod_tack_fillet + float_height / 2
magnet_highest_z = interior_ceiling_z - float_height / 2

# [3 mm](WALL_PRELOAD) — how far the rod pushes the donut past the
# bore wall, which is what holds the magnet-to-wall gap at zero.
donut_wall_preload = (register_radius + donut_od / 2 - tube_id / 2) * 25.4


# ═══════════════════════════════════════════════════════
# BRIDGE
# ═══════════════════════════════════════════════════════

# [14 mm](REED_GLASS_L) × ⌀[2.5 mm](REED_GLASS_D) — Gebildet B0CW9418F6
# glass envelope, diameter taken at the top of the supplier's range.
reed_glass_length = 14.0
reed_glass_diameter = 2.5

seat_clearance = 0.05
inner_radius = tank_outer_radius + seat_clearance
skirt_thickness = 0.8
copper_clearance_over_glass = 0.5
# [3 mm](POCKET_DEPTH) — plateau face to vessel wall; a wrap crossing the
# plateau clears the glass by copper_clearance_over_glass.
pocket_depth = reed_glass_diameter + copper_clearance_over_glass
plateau_radius = tank_outer_radius + pocket_depth
skirt_radius = inner_radius + skirt_thickness

pocket_length = reed_glass_length + 2.0
pocket_width = reed_glass_diameter + 0.5
pocket_end_wall = 3.0
plateau_z_bottom = reed_low_z - pocket_length / 2 - pocket_end_wall
plateau_z_top = reed_high_z + pocket_length / 2 + pocket_end_wall

# Long enough that a wrap dragged down the vessel rides over the step
# instead of catching it, and that the copper's bend radius over the
# circumferential ramp stays well clear of the 1/4" tube's minimum.
axial_ramp_length = 10.0
arc_ramp_width = 16.0
bridge_z_bottom = plateau_z_bottom - axial_ramp_length
bridge_z_top = plateau_z_top + axial_ramp_length
bridge_height = bridge_z_top - bridge_z_bottom

lead_groove_width = 5.6  # three 22 AWG silicone conductors side by side
lead_groove_depth = plateau_radius - skirt_radius
lead_groove_y = 5.4
lead_notch_length = 2.0

plateau_half_width = lead_groove_y + lead_groove_width / 2 + 1.5
bridge_half_width = plateau_half_width + arc_ramp_width

plateau_half_angle = math.asin(plateau_half_width / plateau_radius)
bridge_half_angle = math.asin(bridge_half_width / plateau_radius)

# Copper the bridge carries instead of the wall: every wrap whose
# centreline lands in bridge_height, over the plateau at full
# pocket_depth and over the ramps at half of it.
wraps_carried = bridge_height / pitch
effective_lift_arc = 2 * plateau_half_width + arc_ramp_width
carried_copper = wraps_carried * effective_lift_arc

overcut = 1.0


def _ridge_ring():
    """Revolved profile giving the axial ramps: a skirt_thickness band over
    the whole height, standing to plateau_radius between the two ramps."""
    return (
        cq.Workplane("XZ")
        .polyline([
            (inner_radius, bridge_z_bottom),
            (skirt_radius, bridge_z_bottom),
            (plateau_radius, plateau_z_bottom),
            (plateau_radius, plateau_z_top),
            (skirt_radius, bridge_z_top),
            (inner_radius, bridge_z_top),
        ])
        .close()
        .revolve(360)
    )


def _plan_outline_radius(angle):
    if abs(angle) <= plateau_half_angle:
        return plateau_radius
    fraction = (abs(angle) - plateau_half_angle) / (bridge_half_angle - plateau_half_angle)
    return plateau_radius - fraction * (plateau_radius - skirt_radius)


def _bump_prism():
    """Extrusion along Z of the plan-view outline: plateau_radius across the
    plateau, ramping to skirt_radius at each circumferential edge."""
    steps = 48
    outline = [(0.0, 0.0)]
    for i in range(steps + 1):
        angle = -bridge_half_angle + 2 * bridge_half_angle * i / steps
        radius = _plan_outline_radius(angle)
        outline.append((radius * math.cos(angle), radius * math.sin(angle)))
    return (
        cq.Workplane("XY")
        .workplane(offset=bridge_z_bottom - overcut)
        .polyline(outline)
        .close()
        .extrude(bridge_height + 2 * overcut)
    )


def _radial_box(x_range, y_range, z_range):
    x_min, x_max = x_range
    y_min, y_max = y_range
    z_min, z_max = z_range
    return (
        cq.Workplane("XY")
        .workplane(offset=z_min)
        .moveTo(x_min, y_min)
        .rect(x_max - x_min, y_max - y_min, centered=False)
        .extrude(z_max - z_min)
    )


def _reed_pocket(reed_z):
    """Slot cut clear through to the wall, so the glass lands on bare 316L."""
    return _radial_box(
        (inner_radius - overcut, plateau_radius + overcut),
        (-pocket_width / 2, pocket_width / 2),
        (reed_z - pocket_length / 2, reed_z + pocket_length / 2),
    )


def _lead_notch(z_min):
    """Cross-cut at a pocket end, taking that reed's lead out to the groove."""
    return _radial_box(
        (skirt_radius, plateau_radius + overcut),
        (-pocket_width / 2, lead_groove_y + lead_groove_width / 2),
        (z_min, z_min + lead_notch_length),
    )


def _lead_groove():
    return _radial_box(
        (skirt_radius, plateau_radius + overcut),
        (lead_groove_y - lead_groove_width / 2, lead_groove_y + lead_groove_width / 2),
        (plateau_z_bottom, bridge_z_top + overcut),
    )


def build_reed_bridge():
    bridge = _ridge_ring().intersect(_bump_prism())
    for reed_z in (reed_low_z, reed_high_z):
        bridge = bridge.cut(_reed_pocket(reed_z))
        bridge = bridge.cut(_lead_notch(reed_z - pocket_length / 2))
        bridge = bridge.cut(_lead_notch(reed_z + pocket_length / 2 - lead_notch_length))
    return bridge.cut(_lead_groove())


# ═══════════════════════════════════════════════════════
# SETTING GAUGE (shop tooling, not per-build)
# ═══════════════════════════════════════════════════════

gauge_arc_degrees = 60.0
gauge_wall = 2.0
gauge_hook_depth = 3.5
gauge_hook_height = 4.0


def build_setting_gauge():
    """Band that hangs on the tube's bottom rim; its top face is where the
    bridge's bottom edge goes."""
    return (
        cq.Workplane("XZ")
        .polyline([
            (inner_radius - gauge_hook_depth, -gauge_hook_height),
            (inner_radius + gauge_wall, -gauge_hook_height),
            (inner_radius + gauge_wall, bridge_z_bottom),
            (inner_radius, bridge_z_bottom),
            (inner_radius, 0.0),
            (inner_radius - gauge_hook_depth, 0.0),
        ])
        .close()
        .revolve(gauge_arc_degrees)
    )


def _report(name, shape):
    solids = shape.solids().vals()
    assert len(solids) == 1, f"{name}: expected 1 solid, got {len(solids)}"
    solid = solids[0]
    bb = solid.BoundingBox()
    print(
        f"-> {name}  "
        f"X[{bb.xmin:7.2f}..{bb.xmax:7.2f}] "
        f"Y[{bb.ymin:7.2f}..{bb.ymax:7.2f}] "
        f"Z[{bb.zmin:7.2f}..{bb.zmax:7.2f}]  "
        f"vol {solid.Volume():.0f} mm^3  valid={solid.isValid()}"
    )
    return solid


def main():
    assert reed_low_z > magnet_lowest_z, "low reed below the donut's reach"
    assert reed_high_z < magnet_highest_z, "high reed above the donut's reach"
    assert band_bottom_z < bridge_z_bottom and bridge_z_top < band_top_z, \
        "bridge runs outside the wind band"
    assert reed_glass_length > inter_wrap_clear, \
        "reed fits between wraps; the bridge is unnecessary"

    print(f"Wind band on the tube:  {band_bottom_z:.1f} .. {band_top_z:.1f} mm "
          f"(pitch {pitch:.3f}, clear channel {inter_wrap_clear:.3f})")
    print(f"Wetted column:          {interior_floor_z:.2f} .. {interior_ceiling_z:.2f} mm "
          f"= {interior_height:.2f} mm, {volume_per_mm:.3f} mL/mm, {interior_volume_ml:.0f} mL")
    print(f"Serving:                {carbonated_water_per_serving:.1f} mL water "
          f"= {serving_level_rise:.2f} mm of level")
    print(f"CHI (pump off):         level {high_level_z:.2f} mm  "
          f"stored {stored_ml:.0f} mL = {stored_ml / carbonated_water_per_serving:.2f} servings, "
          f"headspace {headspace_ml:.0f} mL ({100 - 100 * high_fill_fraction:.0f} %)")
    print(f"CLO (pump on):          level {low_level_z:.2f} mm  "
          f"reserve {reserve_ml:.0f} mL = {reserve_ml / carbonated_water_per_serving:.2f} servings, "
          f"band {serving_level_rise:.2f} mm = 1.00 serving")
    print(f"Donut mid-plane reach:  {magnet_lowest_z:.1f} .. {magnet_highest_z:.1f} mm "
          f"(wall preload {donut_wall_preload:.2f} mm)")
    print(f"Bridge:                 Z {bridge_z_bottom:.2f} .. {bridge_z_top:.2f} "
          f"({bridge_height:.2f} mm), arc {2 * bridge_half_width:.1f} mm, "
          f"{pocket_depth:.1f} mm proud")
    print(f"Copper carried:         {wraps_carried:.2f} wraps x {effective_lift_arc:.1f} mm "
          f"= {carried_copper:.0f} mm")

    out_dir = _here.parent
    bridge = build_reed_bridge()
    gauge = build_setting_gauge()
    bridge_solid = _report("reed-bridge.step", bridge)
    gauge_solid = _report("reed-bridge-setting-gauge.step", gauge)
    export_step(bridge, str(out_dir / "reed-bridge.step"))
    export_step(gauge, str(out_dir / "reed-bridge-setting-gauge.step"))

    variables = {
        "BAND_BOTTOM": f"{band_bottom_z:.4g} mm",
        "BAND_TOP": f"{band_top_z:.4g} mm",
        "WRAP_PITCH": f"{pitch:.4g} mm",
        "COPPER_OD": f"{copper_od:.4g} mm",
        "INTER_WRAP_CLEAR": f"{inter_wrap_clear:.4g} mm",
        "INTERIOR_FLOOR": f"{interior_floor_z:.4g} mm",
        "INTERIOR_CEILING": f"{interior_ceiling_z:.4g} mm",
        "INTERIOR_H": f"{interior_height:.4g} mm",
        "TUBE_ID_MM": f"{tube_id_mm:.4g} mm",
        "ML_PER_MM": f"{volume_per_mm:.4g} mL",
        "INTERIOR_ML": f"{interior_volume_ml:.4g} mL",
        "WATER_PER_SERVING": f"{carbonated_water_per_serving:.4g} mL",
        "SERVING_RISE": f"{serving_level_rise:.4g} mm",
        "HIGH_LEVEL": f"{high_level_z:.4g} mm",
        "LOW_LEVEL": f"{low_level_z:.4g} mm",
        "HEADSPACE_ML": f"{headspace_ml:.4g} mL",
        "RESERVE_ML": f"{reserve_ml:.4g} mL",
        "RESERVE_SERVINGS": f"{reserve_ml / carbonated_water_per_serving:.3g}",
        "STORED_ML": f"{stored_ml:.4g} mL",
        "STORED_SERVINGS": f"{stored_ml / carbonated_water_per_serving:.3g}",
        "MAGNET_LOWEST": f"{magnet_lowest_z:.4g} mm",
        "MAGNET_HIGHEST": f"{magnet_highest_z:.4g} mm",
        "WALL_PRELOAD": f"{donut_wall_preload:.3g} mm",
        "DONUT_OD": f"{donut_od * 25.4:.4g} mm",
        "REED_GLASS_L": f"{reed_glass_length:.4g} mm",
        "REED_GLASS_D": f"{reed_glass_diameter:.4g} mm",
        "POCKET_DEPTH": f"{pocket_depth:.4g} mm",
        "POCKET_L": f"{pocket_length:.4g} mm",
        "POCKET_W": f"{pocket_width:.4g} mm",
        "SKIRT_T": f"{skirt_thickness:.4g} mm",
        "AXIAL_RAMP": f"{axial_ramp_length:.4g} mm",
        "ARC_RAMP": f"{arc_ramp_width:.4g} mm",
        "BRIDGE_Z_BOTTOM": f"{bridge_z_bottom:.4g} mm",
        "BRIDGE_Z_TOP": f"{bridge_z_top:.4g} mm",
        "BRIDGE_H": f"{bridge_height:.4g} mm",
        "BRIDGE_ARC": f"{2 * bridge_half_width:.4g} mm",
        "EFFECTIVE_ARC": f"{effective_lift_arc:.4g} mm",
        "CARRIED_FRACTION": f"{100 * carried_copper / wrap_length:.2g} %",
        "LEAD_GROOVE_W": f"{lead_groove_width:.4g} mm",
        "LEAD_GROOVE_D": f"{lead_groove_depth:.4g} mm",
        "WRAPS_CARRIED": f"{wraps_carried:.3g}",
        "CARRIED_COPPER": f"{carried_copper:.0f} mm",
        "BRIDGE_VOL": f"{bridge_solid.Volume() / 1000:.3g} cm³",
        "GAUGE_VOL": f"{gauge_solid.Volume() / 1000:.3g} cm³",
        "GAUGE_ARC_DEG": f"{gauge_arc_degrees:.3g}°",
    }
    substitute_md(
        out_dir / "README.md",
        variables=variables,
        expected_counts={
            "BAND_BOTTOM": 1,
            "BAND_TOP": 1,
            "WRAP_PITCH": 1,
            "COPPER_OD": 1,
            "INTER_WRAP_CLEAR": 1,
            "INTERIOR_FLOOR": 1,
            "INTERIOR_CEILING": 1,
            "INTERIOR_H": 1,
            "TUBE_ID_MM": 1,
            "ML_PER_MM": 1,
            "INTERIOR_ML": 1,
            "WATER_PER_SERVING": 1,
            "SERVING_RISE": 1,
            "HIGH_LEVEL": 1,
            "LOW_LEVEL": 1,
            "HEADSPACE_ML": 1,
            "RESERVE_ML": 1,
            "RESERVE_SERVINGS": 1,
            "STORED_ML": 1,
            "STORED_SERVINGS": 1,
            "MAGNET_LOWEST": 1,
            "MAGNET_HIGHEST": 1,
            "WALL_PRELOAD": 1,
            "REED_GLASS_L": 1,
            "REED_GLASS_D": 1,
            "POCKET_DEPTH": 2,
            "POCKET_L": 1,
            "POCKET_W": 1,
            "SKIRT_T": 1,
            "AXIAL_RAMP": 1,
            "ARC_RAMP": 1,
            "BRIDGE_Z_BOTTOM": 2,
            "BRIDGE_Z_TOP": 1,
            "BRIDGE_H": 1,
            "BRIDGE_ARC": 1,
            "EFFECTIVE_ARC": 1,
            "CARRIED_FRACTION": 1,
            "LEAD_GROOVE_W": 1,
            "LEAD_GROOVE_D": 1,
            "WRAPS_CARRIED": 1,
            "CARRIED_COPPER": 1,
            "BRIDGE_VOL": 1,
            "GAUGE_VOL": 1,
            "GAUGE_ARC_DEG": 1,
        },
    )
    print("-> README.md")
    substitute_md(
        out_dir.parent / "reservoir" / "level-sensing.md",
        variables=variables,
        expected_counts={
            "REED_GLASS_L": 1,
            "DONUT_OD": 1,
            "TUBE_ID_MM": 1,
        },
    )
    print("-> ../reservoir/level-sensing.md")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "BAND_BOTTOM": 1,
            "BAND_TOP": 1,
            "WRAP_PITCH": 1,
            "INTER_WRAP_CLEAR": 1,
            "INTERIOR_FLOOR": 1,
            "INTERIOR_CEILING": 1,
            "INTERIOR_H": 1,
            "TUBE_ID_MM": 1,
            "ML_PER_MM": 1,
            "INTERIOR_ML": 1,
            "WATER_PER_SERVING": 1,
            "SERVING_RISE": 1,
            "HIGH_LEVEL": 1,
            "LOW_LEVEL": 1,
            "MAGNET_LOWEST": 1,
            "MAGNET_HIGHEST": 1,
            "WALL_PRELOAD": 1,
            "REED_GLASS_L": 2,
            "REED_GLASS_D": 1,
            "POCKET_DEPTH": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
