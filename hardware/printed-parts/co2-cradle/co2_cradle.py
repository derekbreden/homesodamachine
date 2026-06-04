"""CO2 cradle — instrumented platform the 5 lb CO2 cylinder stands in,
so the appliance reads remaining CO2 by weight. Two printed parts (a
grounded base on three feet, a floating well the cylinder drops into)
bridged by one off-the-shelf single-point load cell.

Frame: world +Z is up; the cylinder axis runs up world Z at world
(X, Y) = (0, 0); world Z=0 is the foot-contact plane (cabinet floor).
The load cell bar lies along world X — fixed end toward -X, free (load)
end toward +X. The regulator/tether notch in the well rim faces world
+Y, toward the front-panel CO2 inlet.

The only load path from cylinder to floor is cylinder -> well -> load
cell -> base -> feet. Nothing else bridges the floating well to the
grounded base, so a leaning cylinder or a tugging CO2 tether adds only a
lateral force the cell does not weigh. Companion: co2-cradle.md."""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cadq_export import export_step, export_assembly
from docgen import substitute_md, substitute_py_comments


# ============================================================
# VOCABULARY
# ============================================================

# CO2 cylinder envelope — [127 mm](CYL_D) ⌀ 5 lb aluminum CGA-320 body.
cylinder_diameter = 127.0
cylinder_radius = cylinder_diameter / 2.0

# [4 mm](SEAT_CLEAR) radial drop-in gap between the well bore and the
# cylinder OD — set the cylinder down, don't thread it in.
seat_radial_clearance = 4.0

# [3.5 mm](WALL_T) — well wall and base structural wall.
wall_thickness = 3.5
# [6 mm](FLOOR_T) — well floor; carries the full cylinder load into the
# free-end riser beneath it.
floor_thickness = 6.0

# WELL — floating cup the cylinder stands in.
well_bore_radius = cylinder_radius + seat_radial_clearance
well_outer_radius = well_bore_radius + wall_thickness
# [110 mm](WELL_WALL_H) wall above the interior floor — captures a
# ~18-inch cylinder against leaning without bearing vertical load; short
# enough to set the cylinder in without lifting it over a tall collar.
well_wall_height = 110.0

# LOAD CELL — single-point "bar" cell, long axis along world X. Envelope
# of a 20 kg Geekstory cell (B079FQNJJH); confirm against the real part.
# Fixed end anchors to the base at -X, free (load) end carries the well
# at +X. [80 mm](CELL_L) × [12.7 mm](CELL_W) × [12.7 mm](CELL_H).
load_cell_length = 80.0
load_cell_width = 12.7
load_cell_height = 12.7
load_cell_end_inset = 6.0
load_cell_end_bolt_pitch = 15.0
load_cell_fastener_radius = 3.0  # M5 seat — insert vs. direct-tap is an open item

# Two mounting bolts at each end, on the bar centerline (world Y=0).
load_cell_free_outer_x = load_cell_length / 2.0 - load_cell_end_inset
load_cell_free_inner_x = load_cell_free_outer_x - load_cell_end_bolt_pitch
load_cell_fixed_outer_x = -load_cell_free_outer_x
load_cell_fixed_inner_x = -load_cell_free_inner_x

# MOUNTING STACK — the single-point bending couple. [8 mm](CELL_AIR_GAP)
# of air under the free end and over the fixed end lets the bar bend.
cell_air_gap = 8.0
fastener_engagement = 6.0  # blind-hole depth for the cell fasteners

# FEET — three at 120°; three points seat flat on any floor with no rock.
# Feet lift the base [10 mm](FOOT_H) off the cabinet floor.
foot_height = 10.0
foot_radius = 9.0
foot_angles_deg = (90.0, 210.0, 330.0)

base_plate_thickness = 6.0
base_overhang = 8.0
base_plate_radius = well_outer_radius + base_overhang

# Z-ladder, foot-contact plane up. The fixed-end pedestal raises the cell
# bottom by the air gap; the cell's own height plus a second air gap sets
# the well underside.
base_plate_top_z = foot_height + base_plate_thickness
cell_bottom_z = base_plate_top_z + cell_air_gap
cell_top_z = cell_bottom_z + load_cell_height
well_underside_z = cell_top_z + cell_air_gap
well_floor_inner_z = well_underside_z + floor_thickness
well_rim_z = well_floor_inner_z + well_wall_height

# TRAVEL STOP — pads flanking the cell in ±Y, rising to [2 mm](TRAVEL_GAP)
# below the well underside. An overload (cylinder dropped in, someone
# leaning) lands the well floor here before the bar over-deflects.
travel_stop_gap = 2.0
travel_stop_top_z = well_underside_z - travel_stop_gap
travel_stop_y = 30.0
travel_stop_radius = 7.0

# Load-cell mount footprints. The fixed-end pedestal and the free-end
# riser each span their end's bolt pair with margin.
mount_x_margin = 6.0
mount_half_width = load_cell_width / 2.0 + 5.0
fixed_mount_x_lo = load_cell_fixed_outer_x - mount_x_margin
fixed_mount_x_hi = load_cell_fixed_inner_x + mount_x_margin
free_mount_x_lo = load_cell_free_inner_x - mount_x_margin
free_mount_x_hi = load_cell_free_outer_x + mount_x_margin

# RIM NOTCH — [46 mm](NOTCH_W) wide × [45 mm](NOTCH_DEPTH) deep gap in the
# +Y wall for the regulator body + CO2 tether; also the orientation index.
notch_width = 46.0
notch_depth = 45.0

# DRAINS — three holes through the well floor (and matching holes through
# the base plate below) so water never pools around the cylinder base.
# Angles dodge the +Y rim notch and the X-aligned cell footprint.
drain_radius = 3.5
drain_ring_radius = well_bore_radius - 8.0
drain_angles_deg = (30.0, 150.0, 270.0)


# ============================================================
# PRIMITIVES
# ============================================================

def _polar(radius, angle_deg):
    """World (x, y) at `radius` and `angle_deg` about the Z axis."""
    a = math.radians(angle_deg)
    return (radius * math.cos(a), radius * math.sin(a))


def _z_cylinder(center_xy, z_range, radius):
    """Solid cylinder, axis along world +Z, centered at (world_x, world_y),
    spanning z_range = (z_bottom, z_top)."""
    x, y = center_xy
    z_bottom, z_top = z_range
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=z_bottom)
        .center(x, y)
        .circle(radius)
        .extrude(z_top - z_bottom)
    ).unwrap()


def _z_box(center_xy, xy_size, z_range):
    """Axis-aligned box, centered at (world_x, world_y), with xy_size =
    (x_width, y_width), spanning z_range = (z_bottom, z_top)."""
    x, y = center_xy
    x_width, y_width = xy_size
    z_bottom, z_top = z_range
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=z_bottom)
        .center(x, y)
        .rect(x_width, y_width)
        .extrude(z_top - z_bottom)
    ).unwrap()


def _z_box_ranges(x_range, y_range, z_range):
    """_z_box from min/max ranges per axis."""
    x_lo, x_hi = min(x_range), max(x_range)
    y_lo, y_hi = min(y_range), max(y_range)
    return _z_box(
        ((x_lo + x_hi) / 2.0, (y_lo + y_hi) / 2.0),
        (x_hi - x_lo, y_hi - y_lo),
        z_range,
    )


def _z_hole(center_xy, z_range, radius):
    """_z_cylinder with a 0.5 mm overshoot at each end for a clean cut."""
    z_bottom, z_top = z_range
    return _z_cylinder(center_xy, (z_bottom - 0.5, z_top + 0.5), radius)


# ============================================================
# WELL — the floating cup
# ============================================================

def _well_cup():
    """Outer cylinder from the underside to the rim, bored from the floor
    top upward — leaves a solid floor and an annular wall."""
    outer = _z_cylinder((0, 0), (well_underside_z, well_rim_z), well_outer_radius)
    bore = _z_cylinder((0, 0), (well_floor_inner_z, well_rim_z + 1.0), well_bore_radius)
    return outer.cut(bore)


def _well_free_riser():
    """Boss hanging from the well underside down to the load cell's free
    (+X) end — the single point delivering the well's weight to the cell."""
    return _z_box_ranges(
        (free_mount_x_lo, free_mount_x_hi),
        (-mount_half_width, mount_half_width),
        (cell_top_z, well_underside_z),
    )


def _well_rim_notch():
    """Regulator/tether gap in the +Y rim, through the wall."""
    return _z_box_ranges(
        (-notch_width / 2.0, notch_width / 2.0),
        (well_bore_radius - 2.0, well_outer_radius + 2.0),
        (well_rim_z - notch_depth, well_rim_z + 1.0),
    )


def build_well():
    """Floating cup + free-end riser, rim notch and floor drains cut."""
    well = _well_cup().union(_well_free_riser())
    well = well.cut(_well_rim_notch())
    for x in (load_cell_free_outer_x, load_cell_free_inner_x):
        well = well.cut(_z_hole((x, 0), (cell_top_z, cell_top_z + fastener_engagement),
                                load_cell_fastener_radius))
    for angle in drain_angles_deg:
        well = well.cut(_z_hole(_polar(drain_ring_radius, angle),
                                (well_underside_z, well_floor_inner_z), drain_radius))
    return well


# ============================================================
# BASE — the grounded reference
# ============================================================

def _base_feet():
    """Three feet at 120° under the base plate."""
    feet = None
    for angle in foot_angles_deg:
        foot = _z_cylinder(_polar(base_plate_radius - foot_radius - 3.0, angle),
                           (0.0, foot_height), foot_radius)
        feet = foot if feet is None else feet.union(foot)
    return feet


def _base_fixed_pedestal():
    """Pedestal the load cell's fixed (-X) end bolts down to."""
    return _z_box_ranges(
        (fixed_mount_x_lo, fixed_mount_x_hi),
        (-mount_half_width, mount_half_width),
        (base_plate_top_z, cell_bottom_z),
    )


def _base_travel_stops():
    """Two pads flanking the cell in ±Y, rising to travel_stop_top_z."""
    return _z_cylinder((0, travel_stop_y), (base_plate_top_z, travel_stop_top_z), travel_stop_radius).union(
        _z_cylinder((0, -travel_stop_y), (base_plate_top_z, travel_stop_top_z), travel_stop_radius)
    )


def build_base():
    """Disc on three feet, fixed-end pedestal + travel-stop pads on top,
    fixed-end fastener pockets and floor drains cut."""
    base = _z_cylinder((0, 0), (foot_height, base_plate_top_z), base_plate_radius)
    base = base.union(_base_feet()).union(_base_fixed_pedestal()).union(_base_travel_stops())
    for x in (load_cell_fixed_outer_x, load_cell_fixed_inner_x):
        base = base.cut(_z_hole((x, 0), (cell_bottom_z - fastener_engagement, cell_bottom_z),
                                load_cell_fastener_radius))
    for angle in drain_angles_deg:
        base = base.cut(_z_hole(_polar(drain_ring_radius, angle),
                                (foot_height, base_plate_top_z), drain_radius))
    return base


# ============================================================
# REFERENCE — off-the-shelf cell envelope, for fit visualization
# ============================================================

def build_load_cell_reference():
    """The off-the-shelf single-point cell envelope, in place — NOT a
    printed part. Shows the air gaps above and below the bar."""
    return _z_box((0, 0), (load_cell_length, load_cell_width), (cell_bottom_z, cell_top_z))


def build_reference_assembly():
    """Base + well + load-cell reference, each in its world position."""
    assembly = cq.Assembly()
    assembly.add(build_base(), name="base", color=cq.Color(0.72, 0.72, 0.74))
    assembly.add(build_well(), name="well", color=cq.Color(0.55, 0.70, 0.85))
    assembly.add(build_load_cell_reference(), name="load-cell-ref", color=cq.Color(0.90, 0.55, 0.20))
    return assembly


def main():
    out_dir = Path(__file__).resolve().parent
    base = build_base()
    well = build_well()
    assembly = build_reference_assembly()

    base_out = out_dir / "co2-cradle-base.step"
    well_out = out_dir / "co2-cradle-well.step"
    assembly_out = out_dir / "co2-cradle.step"
    export_step(base, str(base_out))
    export_step(well, str(well_out))
    export_assembly(assembly, str(assembly_out))
    print(f"-> {base_out.name}")
    print(f"-> {well_out.name}")
    print(f"-> {assembly_out.name}")

    def mm(value):
        return f"{value:.4g} mm"

    variables = {
        "CYL_D": mm(cylinder_diameter),
        "SEAT_CLEAR": mm(seat_radial_clearance),
        "WALL_T": mm(wall_thickness),
        "FLOOR_T": mm(floor_thickness),
        "WELL_ID": mm(2.0 * well_bore_radius),
        "WELL_OD": mm(2.0 * well_outer_radius),
        "WELL_WALL_H": mm(well_wall_height),
        "BASE_OD": mm(2.0 * base_plate_radius),
        "PLATFORM_H": mm(well_rim_z),
        "CELL_L": mm(load_cell_length),
        "CELL_W": mm(load_cell_width),
        "CELL_H": mm(load_cell_height),
        "CELL_AIR_GAP": mm(cell_air_gap),
        "TRAVEL_GAP": mm(travel_stop_gap),
        "FOOT_H": mm(foot_height),
        "NOTCH_W": mm(notch_width),
        "NOTCH_DEPTH": mm(notch_depth),
    }
    substitute_md(
        out_dir / "co2-cradle.md",
        variables=variables,
        expected_counts={
            "CYL_D": 1,
            "SEAT_CLEAR": 1,
            "WELL_ID": 1,
            "WELL_OD": 2,
            "WALL_T": 1,
            "FLOOR_T": 1,
            "WELL_WALL_H": 1,
            "NOTCH_W": 1,
            "NOTCH_DEPTH": 1,
            "BASE_OD": 1,
            "FOOT_H": 1,
            "CELL_AIR_GAP": 1,
            "TRAVEL_GAP": 1,
            "CELL_L": 1,
            "CELL_W": 1,
            "CELL_H": 1,
        },
    )
    print("-> co2-cradle.md")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "CYL_D": 1,
            "SEAT_CLEAR": 1,
            "WALL_T": 1,
            "FLOOR_T": 1,
            "WELL_WALL_H": 1,
            "CELL_L": 1,
            "CELL_W": 1,
            "CELL_H": 1,
            "CELL_AIR_GAP": 1,
            "TRAVEL_GAP": 1,
            "FOOT_H": 1,
            "NOTCH_W": 1,
            "NOTCH_DEPTH": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
